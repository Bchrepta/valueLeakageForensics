"""Thought Anchors–style resampling on a finished local Donation Bet run.

For each incentive rollout with a detected revision cut:
  - keep assistant prefix before the first revision/threshold cue
  - regenerate the remainder K times
  - measure how often the final estimate lands on the good vs bad side

  python -m analysis.local_qwen.resample --run_dir analysis/local_qwen/runs/<stamp> --k 8
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analysis.local_qwen.prompts_and_parse import (
    SYSTEM_PROMPTS,
    GenConfig,
    LocalLM,
    build_user_prompt,
    final_estimate,
    first_revision_cut,
    side,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", type=Path, required=True)
    ap.add_argument("--k", type=int, default=8, help="resamples per cut")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--load_in_4bit", action="store_true")
    ap.add_argument("--max_rollouts", type=int, default=12, help="cap traces to resample")
    ap.add_argument("--max_new_tokens", type=int, default=512)
    args = ap.parse_args()

    run_dir: Path = args.run_dir
    cfg_path = run_dir / "config.json"
    thr = json.loads((run_dir / "threshold.json").read_text())["threshold"]
    cfg_j = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    model_name = cfg_j.get("model", "Qwen/Qwen2.5-3B-Instruct")
    system_key = cfg_j.get("system_prompt", "none")
    system = SYSTEM_PROMPTS.get(system_key)

    lm = LocalLM(
        GenConfig(
            model=model_name,
            device=args.device,
            max_new_tokens=args.max_new_tokens,
            load_in_4bit=args.load_in_4bit,
        )
    )

    results = []
    for cond in ("above_good", "below_good"):
        rows = json.loads((run_dir / f"{cond}.json").read_text())["rows"]
        user = build_user_prompt(cond, thr)
        used = 0
        for row in rows:
            if used >= args.max_rollouts:
                break
            text = row.get("text") or ""
            cut = first_revision_cut(text)
            if not cut:
                continue
            prefix, _suffix = cut
            orig_est = row.get("estimate") or final_estimate(text)
            if orig_est is None:
                continue
            orig_side = side(orig_est, thr, cond)
            resampled = []
            for j in range(args.k):
                new_text = lm.continue_from(user, prefix, system=system)
                est = final_estimate(new_text)
                if est is None:
                    resampled.append({"j": j, "estimate": None, "side": None})
                    continue
                resampled.append(
                    {
                        "j": j,
                        "estimate": est,
                        "side": side(est, thr, cond),
                    }
                )
            valid = [r for r in resampled if r["side"]]
            frac_good = (
                sum(1 for r in valid if r["side"] == "good") / len(valid) if valid else None
            )
            frac_flip = (
                sum(1 for r in valid if r["side"] != orig_side) / len(valid) if valid else None
            )
            results.append(
                {
                    "condition": cond,
                    "i": row["i"],
                    "orig_estimate": orig_est,
                    "orig_side": orig_side,
                    "prefix_chars": len(prefix),
                    "k": args.k,
                    "frac_good": frac_good,
                    "frac_flip_from_orig": frac_flip,
                    "resampled": resampled,
                }
            )
            used += 1
            print(
                f"{cond}[{row['i']}] orig={orig_est:.0f} ({orig_side}) "
                f"frac_good={frac_good} frac_flip={frac_flip}"
            )

    out = {
        "run_dir": str(run_dir),
        "threshold": thr,
        "k": args.k,
        "n_traces": len(results),
        "mean_frac_flip": (
            sum(r["frac_flip_from_orig"] for r in results if r["frac_flip_from_orig"] is not None)
            / max(1, sum(1 for r in results if r["frac_flip_from_orig"] is not None))
        ),
        "traces": results,
    }
    out_path = run_dir / "resample_summary.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in out if k != "traces"}, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
