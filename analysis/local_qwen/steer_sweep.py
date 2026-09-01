"""Hardened Donation-Bet steering sweeps (Gilg-lite).

Direction modes:
  condition  — last *prompt* token: act(above_good) − act(below_good)
  outcome    — last *assistant* token on stored rollouts: mean(good-side) − mean(bad-side)
  parked     — last assistant token: mean(parked@thr) − mean(non-parked)

Primary metric: frac_parked (not MRF-proxy). Always includes random-direction control.

Examples (3080):

  # Layer × alpha sweep with outcome direction (recommended)
  python -m analysis.local_qwen.steer_sweep \\
      --run_dir analysis/local_qwen/runs/Qwen2.5-3B-Instruct_20260827_223600 \\
      --model Qwen/Qwen2.5-3B-Instruct --device cuda --n 12 \\
      --direction outcome --layers 6,12,18,24,30 --alphas -0.6,-0.4,-0.2,0,0.2

  # Parked-vs-not direction at best layer
  python -m analysis.local_qwen.steer_sweep \\
      --run_dir ... --direction parked --layers 18 --alphas -0.4,0 --n 16
"""

from __future__ import annotations

import argparse
import json
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
    side,
    summarize_condition,
)
from analysis.local_qwen.steer_turnoff import SteeringHook, generate_steered


def _chat_ids(lm: LocalLM, user: str, system: str | None, assistant: str | None = None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    if assistant is None:
        prompt = lm.tok.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        messages.append({"role": "assistant", "content": assistant})
        prompt = lm.tok.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
    inputs = lm.tok(prompt, return_tensors="pt")
    device = lm.model.device
    return {k: v.to(device) for k, v in inputs.items()}


def hidden_last(lm: LocalLM, user: str, system: str | None, layer: int,
                assistant: str | None = None) -> torch.Tensor:
    inputs = _chat_ids(lm, user, system, assistant)
    with torch.no_grad():
        out = lm.model(**inputs, output_hidden_states=True, use_cache=False)
    h = out.hidden_states[layer + 1]
    return h[0, -1, :].detach().float().cpu()


def build_condition_direction(lm, thr, layer, system) -> tuple[torch.Tensor, dict]:
    ua = build_user_prompt("above_good", thr)
    ub = build_user_prompt("below_good", thr)
    a = hidden_last(lm, ua, system, layer)
    b = hidden_last(lm, ub, system, layer)
    d = a - b
    meta = {"mode": "condition", "norm": float(d.norm()), "layer": layer}
    d = d / (d.norm() + 1e-8)
    return d, meta


def build_rollout_direction(
    lm: LocalLM,
    run_dir: Path,
    thr: float,
    layer: int,
    system: str | None,
    mode: str,
) -> tuple[torch.Tensor, dict]:
    """outcome: good-side vs bad-side; parked: ==thr vs not."""
    pos, neg = [], []
    counts = {"pos": 0, "neg": 0, "skip": 0}
    for cond in ("above_good", "below_good"):
        path = run_dir / f"{cond}.json"
        if not path.exists():
            continue
        user = build_user_prompt(cond, int(thr))
        rows = json.loads(path.read_text())["rows"]
        for r in rows:
            text = r.get("text") or ""
            est = r.get("estimate")
            if est is None or not text.strip():
                counts["skip"] += 1
                continue
            parked = abs(est - thr) <= 1.0
            good = side(est, thr, cond) == "good"
            if mode == "outcome":
                take_pos = good
            elif mode == "parked":
                take_pos = parked
            else:
                raise ValueError(mode)
            try:
                h = hidden_last(lm, user, system, layer, assistant=text)
            except Exception as e:
                print(f"  skip forward: {e}")
                counts["skip"] += 1
                continue
            if take_pos:
                pos.append(h)
                counts["pos"] += 1
            else:
                neg.append(h)
                counts["neg"] += 1
    if len(pos) < 2 or len(neg) < 2:
        raise SystemExit(
            f"Need ≥2 pos and ≥2 neg acts for mode={mode}; got {counts}"
        )
    mu_p = torch.stack(pos).mean(0)
    mu_n = torch.stack(neg).mean(0)
    d = mu_p - mu_n
    meta = {
        "mode": mode,
        "layer": layer,
        "n_pos": len(pos),
        "n_neg": len(neg),
        "norm": float(d.norm()),
        "counts": counts,
    }
    d = d / (d.norm() + 1e-8)
    return d, meta


def arm_metrics(rows_by_cond: dict, thr: float) -> dict:
    summary = {
        "above_good": summarize_condition(
            [r["estimate"] for r in rows_by_cond["above_good"]], thr, "above_good"
        ),
        "below_good": summarize_condition(
            [r["estimate"] for r in rows_by_cond["below_good"]], thr, "below_good"
        ),
    }
    summary["mrf_proxy"] = mrf_proxy(summary["above_good"], summary["below_good"])
    parked_rates = []
    for cond in ("above_good", "below_good"):
        ests = [r["estimate"] for r in rows_by_cond[cond] if r["estimate"] is not None]
        parked = sum(1 for e in ests if abs(e - thr) <= 1.0)
        rate = parked / len(ests) if ests else None
        summary[f"{cond}_frac_parked"] = rate
        if rate is not None:
            parked_rates.append(rate)
    summary["mean_frac_parked"] = (
        sum(parked_rates) / len(parked_rates) if parked_rates else None
    )
    return summary


def run_arm(lm, thr, system, direction, alpha, layer, n, name, out_dir) -> dict:
    print(f"=== {name} alpha={alpha} layer={layer} ===")
    rows_by_cond = {}
    for cond in ("above_good", "below_good"):
        user = build_user_prompt(cond, int(thr))
        rows = []
        for i in range(n):
            if abs(alpha) < 1e-12 or direction is None:
                text = lm.generate(user, system=system)
            else:
                text = generate_steered(lm, user, system, direction, alpha, layer)
            est = final_estimate(text)
            rows.append({"i": i, "condition": cond, "text": text, "estimate": est})
            print(f"  {name} {cond}[{i}] est={est}")
        rows_by_cond[cond] = rows
        (out_dir / f"{name}_{cond}.json").write_text(json.dumps({"rows": rows}, indent=2))
    summary = arm_metrics(rows_by_cond, thr)
    summary.update({"arm": name, "alpha": alpha, "layer": layer, "threshold": thr})
    print(
        f"  >> mean_frac_parked={summary['mean_frac_parked']} "
        f"mrf_proxy={summary['mrf_proxy']}"
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--n", type=int, default=12, help="rollouts/condition/arm")
    ap.add_argument(
        "--direction",
        default="outcome",
        choices=["condition", "outcome", "parked"],
    )
    ap.add_argument("--layers", default="18", help="comma list, e.g. 6,12,18,24,30")
    ap.add_argument("--alphas", default="-0.4,0", help="comma list")
    ap.add_argument("--load_in_4bit", action="store_true")
    ap.add_argument("--max_new_tokens", type=int, default=1024)
    ap.add_argument("--system_prompt", default="none", choices=list(SYSTEM_PROMPTS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--skip_random", action="store_true")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    thr = float(json.loads((args.run_dir / "threshold.json").read_text())["threshold"])
    cfg = GenConfig(
        model=args.model,
        device=args.device,
        max_new_tokens=args.max_new_tokens,
        load_in_4bit=args.load_in_4bit,
    )
    print(f"Loading {args.model} …")
    lm = LocalLM(cfg)
    n_layers = len(lm.model.model.layers)
    system = SYSTEM_PROMPTS[args.system_prompt]
    layers = [int(x) for x in args.layers.split(",") if x.strip() != ""]
    alphas = [float(x) for x in args.alphas.split(",") if x.strip() != ""]
    for L in layers:
        if L < 0 or L >= n_layers:
            raise SystemExit(f"layer {L} out of range 0..{n_layers-1}")

    tag = f"_{args.tag}" if args.tag else ""
    out_root = args.run_dir / f"steer_sweep_{args.direction}{tag}"
    out_root.mkdir(parents=True, exist_ok=True)

    all_rows = []
    for layer in layers:
        print(f"\n#### Building direction mode={args.direction} layer={layer}")
        if args.direction == "condition":
            d, meta = build_condition_direction(lm, int(thr), layer, system)
        else:
            d, meta = build_rollout_direction(
                lm, args.run_dir, thr, layer, system, args.direction
            )
        print(f"  meta={meta}")
        r = torch.randn_like(d)
        r = r / (r.norm() + 1e-8)
        layer_dir = out_root / f"layer{layer}"
        layer_dir.mkdir(exist_ok=True)
        torch.save({"direction": d, "random": r, "meta": meta}, layer_dir / "direction.pt")

        # zero arm once per layer
        zero = run_arm(lm, thr, system, None, 0.0, layer, args.n, "steer_+0.00", layer_dir)
        zero["direction_mode"] = args.direction
        zero["direction_meta"] = meta
        all_rows.append(zero)

        for a in alphas:
            if abs(a) < 1e-12:
                continue
            s = run_arm(
                lm, thr, system, d, a, layer, args.n, f"steer_{a:+.2f}", layer_dir
            )
            s["direction_mode"] = args.direction
            s["direction_meta"] = meta
            all_rows.append(s)

        if not args.skip_random:
            # random at most-negative |alpha| used
            mag = max((abs(a) for a in alphas if abs(a) > 0), default=0.4)
            s = run_arm(
                lm,
                thr,
                system,
                r,
                -mag,
                layer,
                args.n,
                f"random_{-mag:+.2f}",
                layer_dir,
            )
            s["direction_mode"] = "random"
            s["direction_meta"] = {"matched_to": args.direction, "layer": layer}
            all_rows.append(s)

    # compact table: primary = mean_frac_parked
    table = []
    for row in all_rows:
        table.append(
            {
                "layer": row["layer"],
                "arm": row["arm"],
                "direction_mode": row.get("direction_mode"),
                "mean_frac_parked": row.get("mean_frac_parked"),
                "above_frac_parked": row.get("above_good_frac_parked"),
                "below_frac_parked": row.get("below_good_frac_parked"),
                "above_frac_good": row.get("above_good", {}).get("frac_good_side"),
                "below_frac_good": row.get("below_good", {}).get("frac_good_side"),
                "mrf_proxy": row.get("mrf_proxy"),
            }
        )

    report = {
        "run_dir": str(args.run_dir),
        "model": args.model,
        "threshold": thr,
        "direction": args.direction,
        "layers": layers,
        "alphas": alphas,
        "n": args.n,
        "primary_metric": "mean_frac_parked",
        "table": table,
        "arms": all_rows,
        "note": (
            "Lower mean_frac_parked vs steer_0 and vs random = successful "
            "disruption of threshold parroting. outcome/parked directions use "
            "teacher-forced assistant end-state acts from the base run."
        ),
    }
    out_path = out_root / "sweep_summary.json"
    out_path.write_text(json.dumps(report, indent=2))
    print("\n=== TABLE (mean_frac_parked primary) ===")
    for t in table:
        print(
            f"L{t['layer']} {t['arm']:16} mode={t['direction_mode']:10} "
            f"parked={t['mean_frac_parked']} mrf={t['mrf_proxy']}"
        )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
