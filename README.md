# valueleakageforensics

Offline Phase-1 forensics on the Value Leakage **Donation Bet**: whether bad→good estimate “rescues” under donation incentives look like intentional motivated reasoning vs honest revision.

Data: Aditya Singh’s shipped rollouts ([adsingh-64/value-leakage](https://github.com/adsingh-64/value-leakage)).

```bash
python analysis/crossing.py
# results: docs/ACH.md , labeling_packet/results/ben_labels.csv
```

```
docs/ACH.md              hypotheses + label readout
analysis/crossing.py     trajectory rescue stats
labeling_packet/         rubric, CoT samples, filled labels
vendor/value-leakage/    upstream code + runs/
```

**Result (provisional).** Required auto-rescues (n=102): 52% `intentional_steer`, 39% `mixed`, 9% `honest_revision`. Claude rescues 73% `intentional_steer` vs Claude controls 0%. No causal resampling yet.

Upstream code/data in `vendor/value-leakage` belong to [adsingh-64/value-leakage](https://github.com/adsingh-64/value-leakage). Analysis here is original.
