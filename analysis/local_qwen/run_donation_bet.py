"""Run local Donation Bet (baseline → threshold → above/below_good).

  python -m analysis.local_qwen.run_donation_bet --model Qwen/Qwen2.5-3B-Instruct --n 24 --device cuda
  python -m analysis.local_qwen.run_donation_bet --n 24 --system_prompt ignore_bet --tag turnoff
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path

from analysis.local_qwen.prompts_and_parse import (
    SYSTEM_PROMPTS,
    GenConfig,
    LocalLM,
    build_user_prompt,
    final_estimate,
    mrf_proxy,
    parse_millions,
    summarize_condition,
)

ROOT = Path(__file__).resolve().parents[2]
RUNS = Path(__file__).resolve().parent / "runs"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")
    ap.add_argument("--n", type=int, default=24, help="rollouts per condition")
    ap.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    ap.add_argument("--max_new_tokens", type=int, default=1024)
    ap.add_argument("--load_in_4bit", action="store_true")
    ap.add_argument(
        "--system_prompt",
        default="none",
        choices=list(SYSTEM_PROMPTS),
        help="none | ignore_bet (turn-off) | disclose",
    )
    ap.add_argument("--tag", default="", help="suffix for run folder")
    ap.add_argument(
        "--threshold",
        type=int,
        default=None,
        help="If set, skip baseline and use this threshold",
    )
    args = ap.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = args.model.split("/")[-1]
    tag = f"_{args.tag}" if args.tag else ""
    if args.system_prompt != "none" and not args.tag:
        tag = f"_{args.system_prompt}"
    run_dir = RUNS / f"{name}_{stamp}{tag}"
    run_dir.mkdir(parents=True, exist_ok=True)

    cfg = GenConfig(
        model=args.model,
        device=args.device,
        max_new_tokens=args.max_new_tokens,
        load_in_4bit=args.load_in_4bit,
    )
    (run_dir / "config.json").write_text(
        json.dumps({**asdict_cfg(cfg), "n": args.n, "system_prompt": args.system_prompt}, indent=2)
    )

    print(f"Loading {args.model} on {args.device} …")
    lm = LocalLM(cfg)
    system = SYSTEM_PROMPTS[args.system_prompt]

    def sample_condition(cond: str, thr: int | None) -> list[dict]:
        user = build_user_prompt(cond, thr)
        rows = []
        for i in range(args.n):
            text = lm.generate(user, system=system)
            est = final_estimate(text)
            traj = parse_millions(text)
            rows.append(
                {
                    "i": i,
                    "condition": cond,
                    "text": text,
                    "estimate": est,
                    "trajectory": traj,
                }
            )
            print(f"  {cond}[{i}] est={est}")
        (run_dir / f"{cond}.json").write_text(json.dumps({"rows": rows}, indent=2))
        return rows

    base_rows: list[dict] = []
    if args.threshold is None:
        print("=== baseline ===")
        base_rows = sample_condition("baseline", None)
        base_ests = [r["estimate"] for r in base_rows]
        valid = [e for e in base_ests if e is not None]
        if not valid:
            raise SystemExit("No baseline estimates parsed — aborting")
        thr = int(round(statistics.median(valid)))
    else:
        thr = args.threshold
        print(f"Using fixed threshold={thr:,}")

    (run_dir / "threshold.json").write_text(json.dumps({"threshold": thr}, indent=2))
    print(f"threshold = {thr:,}")

    print("=== above_good ===")
    above_rows = sample_condition("above_good", thr)
    print("=== below_good ===")
    below_rows = sample_condition("below_good", thr)

    summary = {
        "model": args.model,
        "system_prompt": args.system_prompt,
        "threshold": thr,
        "baseline": (
            summarize_condition([r["estimate"] for r in base_rows], thr, "baseline")
            if base_rows
            else {"skipped": True}
        ),
        "above_good": summarize_condition(
            [r["estimate"] for r in above_rows], thr, "above_good"
        ),
        "below_good": summarize_condition(
            [r["estimate"] for r in below_rows], thr, "below_good"
        ),
    }
    summary["mrf_proxy"] = mrf_proxy(summary["above_good"], summary["below_good"])
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"Wrote {run_dir}")


def asdict_cfg(cfg: GenConfig) -> dict:
    return {
        "model": cfg.model,
        "device": cfg.device,
        "max_new_tokens": cfg.max_new_tokens,
        "temperature": cfg.temperature,
        "top_p": cfg.top_p,
        "load_in_4bit": cfg.load_in_4bit,
    }


if __name__ == "__main__":
    main()
