"""Option 1 — Gilg-style predict + causally mediate on Donation Bet.

Neel ask (Value Leakage): find a linear direction that *predicts* the effect
and *causally mediates* it (Gilg et al preference-vector family).

This script does both halves on an existing local run (recommended: Qwen3-4B):

  1) PREDICT — leave-one-out mean-diff probe at last assistant token
     (outcome direction). Primary: AUROC for good-side vs bad-side.
     Also reports condition-prompt AUROC at last user token (sanity).

  2) CAUSAL  — steer −α·d / 0 / random on fresh rollouts.
     Primary metrics: above/below frac_good + mrf_proxy (NOT parked%).
     Parked rates reported as secondary confound checks.

Example (3080):

  python -m analysis.local_qwen.gilg_mediate \\
      --run_dir analysis/local_qwen/runs/Qwen3-4B_20260828_004946_qwen3_4b \\
      --model Qwen/Qwen3-4B --device cuda --load_in_4bit \\
      --layers=12,20,28 --alphas=-0.4,-0.2,0 --n 16 \\
      --exclude_parked --tag option1_gilg
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import torch

from analysis.local_qwen.prompts_and_parse import (
    SYSTEM_PROMPTS,
    GenConfig,
    LocalLM,
    build_user_prompt,
    side,
)
from analysis.local_qwen.steer_sweep import (
    build_condition_direction,
    hidden_last,
    run_arm,
)


def auroc(scores: list[float], labels: list[int]) -> float | None:
    """Mann–Whitney AUROC; labels 1 = positive class."""
    pos = [s for s, y in zip(scores, labels) if y == 1]
    neg = [s for s, y in zip(scores, labels) if y == 0]
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for n in neg:
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def accuracy_at_0(scores: list[float], labels: list[int]) -> float | None:
    if not scores:
        return None
    correct = sum(1 for s, y in zip(scores, labels) if (s >= 0) == (y == 1))
    return correct / len(scores)


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3 or n != len(ys):
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx < 1e-12 or dy < 1e-12:
        return None
    return num / (dx * dy)


def load_labeled_acts(
    lm: LocalLM,
    run_dir: Path,
    thr: float,
    layer: int,
    system: str | None,
    exclude_parked: bool,
) -> list[dict]:
    """Teacher-forced last-assistant-token acts labeled by final side."""
    rows_out: list[dict] = []
    for cond in ("above_good", "below_good"):
        path = run_dir / f"{cond}.json"
        if not path.exists():
            continue
        user = build_user_prompt(cond, int(thr))
        for r in json.loads(path.read_text())["rows"]:
            text = r.get("text") or ""
            est = r.get("estimate")
            if est is None or not text.strip():
                continue
            parked = abs(est - thr) <= 1.0
            if exclude_parked and parked:
                continue
            good = side(est, thr, cond) == "good"
            try:
                h = hidden_last(lm, user, system, layer, assistant=text)
            except Exception as e:
                print(f"  skip forward: {e}")
                continue
            rows_out.append(
                {
                    "condition": cond,
                    "estimate": est,
                    "parked": parked,
                    "label_good": int(good),
                    "act": h,
                }
            )
    return rows_out


def loo_outcome_probe(rows: list[dict]) -> dict:
    """Leave-one-out mean-diff probe: score = act · normalize(μ_good − μ_bad)."""
    if sum(r["label_good"] for r in rows) < 2 or sum(1 - r["label_good"] for r in rows) < 2:
        return {
            "n": len(rows),
            "n_pos": sum(r["label_good"] for r in rows),
            "n_neg": sum(1 - r["label_good"] for r in rows),
            "auroc": None,
            "acc_at_0": None,
            "pearson": None,
            "error": "need ≥2 pos and ≥2 neg",
        }
    scores: list[float] = []
    labels: list[int] = []
    for i, row in enumerate(rows):
        pos = [rows[j]["act"] for j in range(len(rows)) if j != i and rows[j]["label_good"] == 1]
        neg = [rows[j]["act"] for j in range(len(rows)) if j != i and rows[j]["label_good"] == 0]
        if len(pos) < 1 or len(neg) < 1:
            continue
        d = torch.stack(pos).mean(0) - torch.stack(neg).mean(0)
        d = d / (d.norm() + 1e-8)
        scores.append(float(torch.dot(row["act"], d)))
        labels.append(row["label_good"])
    return {
        "n": len(rows),
        "n_pos": sum(r["label_good"] for r in rows),
        "n_neg": sum(1 - r["label_good"] for r in rows),
        "n_scored": len(scores),
        "auroc": auroc(scores, labels),
        "acc_at_0": accuracy_at_0(scores, labels),
        "pearson": pearson(scores, [float(y) for y in labels]),
        "mean_score_pos": (
            sum(s for s, y in zip(scores, labels) if y == 1)
            / max(1, sum(labels))
        ),
        "mean_score_neg": (
            sum(s for s, y in zip(scores, labels) if y == 0)
            / max(1, len(labels) - sum(labels))
        ),
    }


def fit_outcome_direction(rows: list[dict]) -> tuple[torch.Tensor, dict]:
    pos = [r["act"] for r in rows if r["label_good"] == 1]
    neg = [r["act"] for r in rows if r["label_good"] == 0]
    if len(pos) < 2 or len(neg) < 2:
        raise SystemExit(f"Need ≥2 pos/neg for full-fit direction; got {len(pos)}/{len(neg)}")
    d = torch.stack(pos).mean(0) - torch.stack(neg).mean(0)
    meta = {
        "mode": "outcome",
        "n_pos": len(pos),
        "n_neg": len(neg),
        "norm_pre_unit": float(d.norm()),
        "n_parked_in_fit": sum(1 for r in rows if r["parked"]),
    }
    d = d / (d.norm() + 1e-8)
    return d, meta


def condition_prompt_sanity(lm, thr, layer, system) -> dict:
    """Last-user-token above vs below should be linearly separable (sanity)."""
    d, meta = build_condition_direction(lm, int(thr), layer, system)
    ua = build_user_prompt("above_good", int(thr))
    ub = build_user_prompt("below_good", int(thr))
    ha = hidden_last(lm, ua, system, layer)
    hb = hidden_last(lm, ub, system, layer)
    sa = float(torch.dot(ha, d))
    sb = float(torch.dot(hb, d))
    return {
        "layer": layer,
        "score_above_prompt": sa,
        "score_below_prompt": sb,
        "separates": sa > sb,
        "gap": sa - sb,
        "meta": meta,
    }


def causal_asymmetry(summary: dict) -> float | None:
    """Mean good-side rate across conditions (primary leakage proxy for mediation)."""
    a = summary.get("above_good", {}).get("frac_good_side")
    b = summary.get("below_good", {}).get("frac_good_side")
    if a is None or b is None:
        return None
    return 0.5 * (a + b)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run_dir", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--load_in_4bit", action="store_true")
    ap.add_argument("--layers", default="12,20,28", help="comma list")
    ap.add_argument(
        "--causal_layers",
        default="",
        help="layers for steer; default = top-2 by predict AUROC",
    )
    ap.add_argument("--alphas", default="-0.4,-0.2,0", help="use --alphas=-0.4,... on PS")
    ap.add_argument("--n", type=int, default=16, help="fresh rollouts / condition / arm")
    ap.add_argument("--exclude_parked", action="store_true",
                    help="fit/score outcome dir without thr-parked rollouts")
    ap.add_argument("--predict_only", action="store_true")
    ap.add_argument("--skip_random", action="store_true")
    ap.add_argument("--max_new_tokens", type=int, default=1024)
    ap.add_argument("--system_prompt", default="none", choices=list(SYSTEM_PROMPTS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="option1_gilg")
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    thr = float(json.loads((args.run_dir / "threshold.json").read_text())["threshold"])
    system = SYSTEM_PROMPTS[args.system_prompt]
    layers = [int(x) for x in args.layers.split(",") if x.strip() != ""]
    alphas = [float(x) for x in args.alphas.split(",") if x.strip() != ""]

    cfg = GenConfig(
        model=args.model,
        device=args.device,
        max_new_tokens=args.max_new_tokens,
        load_in_4bit=args.load_in_4bit,
    )
    print(f"Loading {args.model} …")
    lm = LocalLM(cfg)
    n_layers = len(lm.model.model.layers)
    for L in layers:
        if L < 0 or L >= n_layers:
            raise SystemExit(f"layer {L} out of range 0..{n_layers - 1}")

    tag = f"_{args.tag}" if args.tag else ""
    out_root = args.run_dir / f"gilg_mediate{tag}"
    out_root.mkdir(parents=True, exist_ok=True)

    # ---------- PREDICT ----------
    predict_rows = []
    print("\n==== PREDICT (LOO outcome probe @ last assistant token) ====")
    for layer in layers:
        print(f"\n## layer {layer}")
        labeled = load_labeled_acts(
            lm, args.run_dir, thr, layer, system, args.exclude_parked
        )
        probe = loo_outcome_probe(labeled)
        sanity = condition_prompt_sanity(lm, thr, layer, system)
        row = {
            "layer": layer,
            "exclude_parked": args.exclude_parked,
            "outcome_loo": probe,
            "condition_prompt_sanity": {
                "separates": sanity["separates"],
                "gap": sanity["gap"],
                "score_above": sanity["score_above_prompt"],
                "score_below": sanity["score_below_prompt"],
            },
        }
        predict_rows.append(row)
        print(
            f"  outcome LOO AUROC={probe.get('auroc')} "
            f"acc@0={probe.get('acc_at_0')} "
            f"n={probe.get('n')} pos/neg={probe.get('n_pos')}/{probe.get('n_neg')}"
        )
        print(
            f"  condition prompt sanity separates={sanity['separates']} "
            f"gap={sanity['gap']:.4f}"
        )

    predict_path = out_root / "predict_summary.json"
    predict_path.write_text(
        json.dumps(
            {
                "run_dir": str(args.run_dir),
                "model": args.model,
                "threshold": thr,
                "exclude_parked": args.exclude_parked,
                "primary_metric": "outcome_loo.auroc",
                "layers": predict_rows,
                "note": (
                    "Outcome probe uses teacher-forced last assistant token on "
                    "stored rollouts (post-reasoning state). Condition-prompt "
                    "sanity uses last user token (above vs below framing)."
                ),
            },
            indent=2,
        )
    )
    print(f"Wrote {predict_path}")

    if args.predict_only:
        print("predict_only set — skipping causal arms.")
        return

    # pick causal layers
    if args.causal_layers.strip():
        causal_layers = [int(x) for x in args.causal_layers.split(",") if x.strip()]
    else:
        ranked = sorted(
            predict_rows,
            key=lambda r: (r["outcome_loo"].get("auroc") is not None,
                           r["outcome_loo"].get("auroc") or -1),
            reverse=True,
        )
        causal_layers = [r["layer"] for r in ranked[:2]]
    print(f"\n==== CAUSAL layers={causal_layers} alphas={alphas} n={args.n} ====")

    all_arms = []
    for layer in causal_layers:
        layer_dir = out_root / f"layer{layer}"
        layer_dir.mkdir(exist_ok=True)
        labeled = load_labeled_acts(
            lm, args.run_dir, thr, layer, system, args.exclude_parked
        )
        d, meta = fit_outcome_direction(labeled)
        r = torch.randn_like(d)
        r = r / (r.norm() + 1e-8)
        torch.save(
            {"direction": d, "random": r, "meta": meta},
            layer_dir / "direction.pt",
        )
        print(f"\n#### layer {layer} direction meta={meta}")

        zero = run_arm(lm, thr, system, None, 0.0, layer, args.n, "steer_+0.00", layer_dir)
        zero["direction_mode"] = "outcome"
        zero["direction_meta"] = meta
        zero["mean_frac_good"] = causal_asymmetry(zero)
        all_arms.append(zero)
        print(
            f"  >> frac_good mean={zero['mean_frac_good']} "
            f"mrf={zero['mrf_proxy']} parked={zero['mean_frac_parked']}"
        )

        for a in alphas:
            if abs(a) < 1e-12:
                continue
            s = run_arm(
                lm, thr, system, d, a, layer, args.n, f"steer_{a:+.2f}", layer_dir
            )
            s["direction_mode"] = "outcome"
            s["direction_meta"] = meta
            s["mean_frac_good"] = causal_asymmetry(s)
            all_arms.append(s)
            print(
                f"  >> frac_good mean={s['mean_frac_good']} "
                f"mrf={s['mrf_proxy']} parked={s['mean_frac_parked']}"
            )

        if not args.skip_random:
            mag = max((abs(a) for a in alphas if abs(a) > 0), default=0.4)
            s = run_arm(
                lm, thr, system, r, -mag, layer, args.n, f"random_{-mag:+.2f}", layer_dir
            )
            s["direction_mode"] = "random"
            s["direction_meta"] = {"matched_to": "outcome", "layer": layer}
            s["mean_frac_good"] = causal_asymmetry(s)
            all_arms.append(s)
            print(
                f"  >> frac_good mean={s['mean_frac_good']} "
                f"mrf={s['mrf_proxy']} parked={s['mean_frac_parked']}"
            )

    table = []
    for row in all_arms:
        table.append(
            {
                "layer": row["layer"],
                "arm": row["arm"],
                "direction_mode": row.get("direction_mode"),
                "mean_frac_good": row.get("mean_frac_good"),
                "above_frac_good": row.get("above_good", {}).get("frac_good_side"),
                "below_frac_good": row.get("below_good", {}).get("frac_good_side"),
                "mrf_proxy": row.get("mrf_proxy"),
                "mean_frac_parked": row.get("mean_frac_parked"),
            }
        )

    report = {
        "run_dir": str(args.run_dir),
        "model": args.model,
        "threshold": thr,
        "exclude_parked": args.exclude_parked,
        "predict_summary": str(predict_path),
        "causal_layers": causal_layers,
        "alphas": alphas,
        "n": args.n,
        "primary_metric": "mean_frac_good",
        "secondary_metrics": ["mrf_proxy", "mean_frac_parked"],
        "success_rule": (
            "Steer −α on outcome dir should lower mean_frac_good and/or mrf_proxy "
            "vs zero AND vs matched random. Predict AUROC should be clearly >0.5."
        ),
        "table": table,
        "arms": all_arms,
        "predict_by_layer": predict_rows,
    }
    out_path = out_root / "mediate_summary.json"
    out_path.write_text(json.dumps(report, indent=2))
    print("\n=== TABLE (mean_frac_good primary) ===")
    for t in table:
        print(
            f"L{t['layer']} {t['arm']:16} mode={t['direction_mode']:8} "
            f"frac_good={t['mean_frac_good']} mrf={t['mrf_proxy']} "
            f"parked={t['mean_frac_parked']}"
        )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
