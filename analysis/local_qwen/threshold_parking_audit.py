"""Audit threshold-parking: fraction of estimates exactly equal to threshold.

  python -m analysis.local_qwen.threshold_parking_audit \\
      --run_dir analysis/local_qwen/runs/<stamp> \\
      [--run_dir analysis/local_qwen/runs/<stamp>_turnoff]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analysis.local_qwen.prompts_and_parse import side


def audit_run(run_dir: Path, atol: float = 1.0) -> dict:
    thr = float(json.loads((run_dir / "threshold.json").read_text())["threshold"])
    out: dict = {"run_dir": str(run_dir), "threshold": thr, "conditions": {}}
    for cond in ("baseline", "above_good", "below_good"):
        path = run_dir / f"{cond}.json"
        if not path.exists():
            continue
        rows = json.loads(path.read_text())["rows"]
        ests = [r.get("estimate") for r in rows]
        valid = [e for e in ests if e is not None]
        parked = [e for e in valid if abs(e - thr) <= atol]
        goods = [e for e in valid if side(e, thr, cond) == "good"] if cond != "baseline" else []
        parked_good = [
            e for e in parked if cond != "baseline" and side(e, thr, cond) == "good"
        ]
        out["conditions"][cond] = {
            "n": len(ests),
            "n_valid": len(valid),
            "n_parked_at_thr": len(parked),
            "frac_parked_at_thr": len(parked) / len(valid) if valid else None,
            "frac_good_side": len(goods) / len(valid) if valid and cond != "baseline" else None,
            "frac_good_that_are_parked": (
                len(parked_good) / len(goods) if goods else None
            ),
            "frac_parked_among_good": (
                len(parked_good) / len(goods) if goods else None
            ),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", type=Path, action="append", required=True)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    reports = [audit_run(p) for p in args.run_dir]
    blob = {"runs": reports}
    text = json.dumps(blob, indent=2)
    print(text)
    out = args.out
    if out is None and len(args.run_dir) == 1:
        out = args.run_dir[0] / "threshold_parking.json"
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
