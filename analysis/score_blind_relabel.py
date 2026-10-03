#!/usr/bin/env python3
"""Score blind_labels.csv against blind_key.json and original ben_labels.csv."""
from __future__ import annotations
import csv, json
from pathlib import Path
from collections import Counter, defaultdict

root = Path(__file__).resolve().parents[1]
blind_dir = root / "labeling_packet" / "blind_relabel"
key = {r["blind_id"]: r for r in json.loads((blind_dir / "blind_key.json").read_text())}
orig = {}
with (root / "labeling_packet" / "results" / "ben_labels.csv").open() as f:
    for row in csv.DictReader(f):
        orig[row["sample_id"]] = row["label"]

blind = list(csv.DictReader((blind_dir / "blind_labels.csv").open()))
filled = [r for r in blind if r.get("label", "").strip()]
if not filled:
    print("No filled blind labels yet.")
    raise SystemExit(0)

by_bucket = defaultdict(Counter)
agree = 0
for r in filled:
    k = key[r["blind_id"]]
    bucket = "RESCUE" if k["auto_bucket"] == "RESCUE" else "CONTROL"
    lab = r["label"].strip()
    by_bucket[bucket][lab] += 1
    if orig.get(k["sample_id"]) == lab:
        agree += 1

print(f"filled={len(filled)}/{len(blind)}  agreement_with_unblinded={agree}/{len(filled)}")
for b, c in sorted(by_bucket.items()):
    n = sum(c.values())
    steer = c.get("intentional_steer", 0)
    print(f"{b}: n={n} intentional_steer={steer}/{n}  full={dict(c)}")
