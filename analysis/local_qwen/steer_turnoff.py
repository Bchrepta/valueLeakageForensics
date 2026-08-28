"""Gilg-lite activation steering turn-off for Donation Bet (3080).

Builds a contrastive residual-stream direction at the last user token:
  d = mean(act | above_good) - mean(act | below_good)
Then regenerates incentive prompts while adding ±α * d (and a random control).

  # Collect direction from an existing run's prompts (re-forward), then steer:
  python -m analysis.local_qwen.steer_turnoff \\
      --run_dir analysis/local_qwen/runs/Qwen2.5-3B-Instruct_20260827_223600 \\
      --model Qwen/Qwen2.5-3B-Instruct --n 24 --device cuda --alpha 0.5

Neel ask: linear direction that predicts / causally mediates value leakage
(Gilg-style; preference vector family — residual direction, not single neuron).
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import torch
from torch import nn

from analysis.local_qwen.prompts_and_parse import (
    SYSTEM_PROMPTS,
    GenConfig,
    LocalLM,
    build_user_prompt,
    final_estimate,
    mrf_proxy,
    summarize_condition,
)


def _last_user_hidden(lm: LocalLM, user: str, system: str | None, layer: int) -> torch.Tensor:
    """Mean-pool is wrong for Gilg-lite; use residual at last prompt token, chosen layer."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    prompt = lm.tok.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = lm.tok(prompt, return_tensors="pt")
    device = lm.model.device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = lm.model(**inputs, output_hidden_states=True, use_cache=False)
    # hidden_states[0]=embed; [i]=after layer i
    h = out.hidden_states[layer + 1]  # (1, seq, d)
    return h[0, -1, :].detach().float().cpu()


def collect_direction(
    lm: LocalLM,
    thr: int,
    layer: int,
    n_per_cond: int,
    system: str | None,
) -> tuple[torch.Tensor, dict]:
    acts_above = []
    acts_below = []
    for i in range(n_per_cond):
        # deterministic prompts — same user text every time; direction is condition contrast
        ua = build_user_prompt("above_good", thr)
        ub = build_user_prompt("below_good", thr)
        acts_above.append(_last_user_hidden(lm, ua, system, layer))
        acts_below.append(_last_user_hidden(lm, ub, system, layer))
        print(f"  collect[{i}]")
    # identical prompts => identical acts; still form d from one forward each
    # Better: use diverse rollouts' *stored* texts? For prompt-level condition
    # contrast, one forward per condition is enough. Use mean of repeats for noise.
    mu_a = torch.stack(acts_above).mean(0)
    mu_b = torch.stack(acts_below).mean(0)
    d = mu_a - mu_b
    d = d / (d.norm() + 1e-8)
    meta = {
        "layer": layer,
        "n_per_cond": n_per_cond,
        "dir_norm_pre_unit": float((mu_a - mu_b).norm()),
        "mu_a_norm": float(mu_a.norm()),
        "mu_b_norm": float(mu_b.norm()),
    }
    return d, meta


def collect_direction_from_rollouts(
    lm: LocalLM,
    run_dir: Path,
    layer: int,
    system: str | None,
    max_n: int,
) -> tuple[torch.Tensor, dict]:
    """Contrast finals that landed good-side vs bad-side within each condition.

    Uses the *same* user prompt per condition (Donation Bet prompts are fixed),
    so activation differs only if system/sampling state differs — for chat
    templates the prompt acts are deterministic. Instead we contrast
    above_good prompt vs below_good prompt (condition framing direction).
    """
    thr = json.loads((run_dir / "threshold.json").read_text())["threshold"]
    return collect_direction(lm, thr, layer, max_n, system)


class SteeringHook:
    def __init__(self, direction: torch.Tensor, alpha: float, layer: int):
        self.direction = direction
        self.alpha = alpha
        self.layer = layer
        self.handle = None

    def _hook(self, module, inputs, output):
        # output: Tensor or tuple
        if isinstance(output, tuple):
            h = output[0]
            rest = output[1:]
        else:
            h = output
            rest = None
        # h: (batch, seq, d)
        d = self.direction.to(device=h.device, dtype=h.dtype)
        # scale by residual RMS for alpha ~ O(1) interpretability
        scale = h.norm(dim=-1, keepdim=True).mean() / (d.norm() + 1e-8)
        h = h + self.alpha * scale * d
        if rest is None:
            return h
        return (h,) + rest

    def attach(self, model: nn.Module):
        # Qwen2: model.model.layers[i]
        layers = model.model.layers
        self.handle = layers[self.layer].register_forward_hook(self._hook)

    def remove(self):
        if self.handle is not None:
            self.handle.remove()
            self.handle = None


def generate_steered(
    lm: LocalLM,
    user: str,
    system: str | None,
    direction: torch.Tensor,
    alpha: float,
    layer: int,
) -> str:
    hook = SteeringHook(direction, alpha, layer)
    hook.attach(lm.model)
    try:
        return lm.generate(user, system=system)
    finally:
        hook.remove()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", type=Path, required=True, help="base run (for threshold)")
    ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--n", type=int, default=24, help="rollouts per condition per arm")
    ap.add_argument("--layer", type=int, default=-1, help="0-indexed; -1 => mid layer")
    ap.add_argument("--alpha", type=float, default=0.4, help="steer strength toward -d (turn off)")
    ap.add_argument("--alphas", type=str, default=None, help="comma list, e.g. -0.4,0,0.4")
    ap.add_argument("--collect_n", type=int, default=4)
    ap.add_argument("--load_in_4bit", action="store_true")
    ap.add_argument("--max_new_tokens", type=int, default=1024)
    ap.add_argument("--system_prompt", default="none", choices=list(SYSTEM_PROMPTS))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    thr = json.loads((args.run_dir / "threshold.json").read_text())["threshold"]
    cfg = GenConfig(
        model=args.model,
        device=args.device,
        max_new_tokens=args.max_new_tokens,
        load_in_4bit=args.load_in_4bit,
    )
    print(f"Loading {args.model} …")
    lm = LocalLM(cfg)
    n_layers = len(lm.model.model.layers)
    layer = args.layer if args.layer >= 0 else n_layers // 2
    system = SYSTEM_PROMPTS[args.system_prompt]

    print(f"Collecting direction at layer {layer}/{n_layers} …")
    d, meta = collect_direction_from_rollouts(
        lm, args.run_dir, layer, system, args.collect_n
    )
    # random control direction
    r = torch.randn_like(d)
    r = r / (r.norm() + 1e-8)

    if args.alphas:
        alphas = [float(x) for x in args.alphas.split(",")]
    else:
        # negative alpha * d with d=above-below aims to reduce above-ish framing
        alphas = [-abs(args.alpha), 0.0, abs(args.alpha)]

    arms = []
    # also random at -|alpha|
    arm_specs = [(f"steer_{a:+.2f}", d, a) for a in alphas]
    arm_specs.append((f"random_{-abs(args.alpha):+.2f}", r, -abs(args.alpha)))

    out_dir = args.run_dir / f"steer_layer{layer}"
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({"direction": d, "random": r, "meta": meta}, out_dir / "direction.pt")

    for name, direction, alpha in arm_specs:
        print(f"=== arm {name} alpha={alpha} ===")
        rows_by_cond = {}
        for cond in ("above_good", "below_good"):
            user = build_user_prompt(cond, thr)
            rows = []
            for i in range(args.n):
                if abs(alpha) < 1e-12:
                    text = lm.generate(user, system=system)
                else:
                    text = generate_steered(lm, user, system, direction, alpha, layer)
                est = final_estimate(text)
                rows.append({"i": i, "condition": cond, "text": text, "estimate": est})
                print(f"  {name} {cond}[{i}] est={est}")
            rows_by_cond[cond] = rows
            (out_dir / f"{name}_{cond}.json").write_text(
                json.dumps({"rows": rows}, indent=2)
            )
        summary = {
            "arm": name,
            "alpha": alpha,
            "layer": layer,
            "threshold": thr,
            "above_good": summarize_condition(
                [r["estimate"] for r in rows_by_cond["above_good"]], thr, "above_good"
            ),
            "below_good": summarize_condition(
                [r["estimate"] for r in rows_by_cond["below_good"]], thr, "below_good"
            ),
        }
        summary["mrf_proxy"] = mrf_proxy(summary["above_good"], summary["below_good"])
        # parking
        for cond in ("above_good", "below_good"):
            ests = [r["estimate"] for r in rows_by_cond[cond] if r["estimate"] is not None]
            parked = sum(1 for e in ests if abs(e - thr) <= 1.0)
            summary[f"{cond}_frac_parked"] = parked / len(ests) if ests else None
        arms.append(summary)
        print(json.dumps(summary, indent=2))

    report = {
        "run_dir": str(args.run_dir),
        "model": args.model,
        "threshold": thr,
        "layer": layer,
        "direction_meta": meta,
        "arms": arms,
        "note": (
            "d = normalize(mean_act(above_good_prompt) - mean_act(below_good_prompt)) "
            "at last prompt token. Negative alpha steers against above-vs-below framing. "
            "Compare mrf_proxy and frac_parked to random-direction control."
        ),
    }
    (out_dir / "steer_summary.json").write_text(json.dumps(report, indent=2))
    print(f"Wrote {out_dir / 'steer_summary.json'}")


if __name__ == "__main__":
    main()
