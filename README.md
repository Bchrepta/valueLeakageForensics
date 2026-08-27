# valueleakageforensics

Phase-1 forensics on **Value Leakage** (Donation Bet): do bad→good estimate “rescues” under donation incentives look like intentional motivated reasoning vs honest revision / unfaithful CoT?

Uses Aditya Singh’s shipped rollouts ([adsingh-64/value-leakage](https://github.com/adsingh-64/value-leakage)). Also relevant to Neel Nanda MATS (Science of Model Character).

## Quick start

```bash
python analysis/crossing.py
# docs/ACH.md — competing hypotheses + human-label readout
# labeling_packet/results/ben_labels.csv — filled labels
```

Optional plots:

```bash
cd vendor/value-leakage && uv sync
uv run python -m value_leakage.plot --run_dir runs/qwen3.5-122b-a10b_20260815_030702
```

## Layout

```
docs/ACH.md                 hypotheses + Phase-1 label results
analysis/crossing.py        trajectory rescue / stay stats
analysis/check_samples/     CoT excerpts for review
analysis/ben_labels_summary.json
labeling_packet/            rubric, samples, filled labels.csv
vendor/value-leakage/       Aditya’s code + shipped runs/
```

## Phase-1 claim (provisional)

Among auto bad→good rescues, hand labels find threshold-dependent steering much more often than pure Fermi revision (Claude rescues **73%** `intentional_steer` vs Claude controls **0%**). Causal sentence resampling not done yet.

## License / attribution

Shipped data and experiment code in `vendor/value-leakage` belong to [adsingh-64/value-leakage](https://github.com/adsingh-64/value-leakage). Analysis code here is original to this repo.
