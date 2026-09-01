"""Compare default vs ignore_bet (turn-off) local runs.

  python -m analysis.local_qwen.compare_turnoff \\
      --base analysis/local_qwen/runs/<stamp> \\
      --turnoff analysis/local_qwen/runs/<stamp>_turnoff
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--turnoff", type=Path, required=True)
    args = ap.parse_args()
    b = json.loads((args.base / "summary.json").read_text())
    t = json.loads((args.turnoff / "summary.json").read_text())
    out = {
        "base_mrf_proxy": b.get("mrf_proxy"),
        "turnoff_mrf_proxy": t.get("mrf_proxy"),
        "delta_mrf_proxy": (
            None
            if b.get("mrf_proxy") is None or t.get("mrf_proxy") is None
            else t["mrf_proxy"] - b["mrf_proxy"]
        ),
        "base_above_frac_good": b.get("above_good", {}).get("frac_good_side"),
        "turnoff_above_frac_good": t.get("above_good", {}).get("frac_good_side"),
        "base_below_frac_good": b.get("below_good", {}).get("frac_good_side"),
        "turnoff_below_frac_good": t.get("below_good", {}).get("frac_good_side"),
        "interpretation": (
            "Turn-off helped (MRF-proxy dropped)"
            if (b.get("mrf_proxy") is not None and t.get("mrf_proxy") is not None and t["mrf_proxy"] < b["mrf_proxy"])
            else "Turn-off did not clearly reduce MRF-proxy (or missing data)"
        ),
    }
    print(json.dumps(out, indent=2))
    (args.turnoff / "turnoff_compare.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
