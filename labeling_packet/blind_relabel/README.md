# Blind Claude relabel

Unblinded Phase-1 labels knew RESCUE vs CONTROL from sample IDs/headers.

This packet: **20 Claude trajectories** (10 auto-RESCUE + 10 CONTROL), shuffled, opaque `B01`… IDs, bucket stripped from the prompt.

1. Label `blind_samples.md` into `blind_labels.csv` **without opening** `blind_key.json`.
2. Then run `python analysis/score_blind_relabel.py` (or compare manually) against the key and original `ben_labels.csv`.

Do not commit filled labels that were made while peeking at the key.
