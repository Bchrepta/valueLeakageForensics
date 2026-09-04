# Value Leakage Forensics

Neel Nanda MATS 12.0 application project (Ben Chrepta).

Offline forensics on Aditya Singh’s [Value Leakage Donation Bet](https://github.com/adsingh-64/value-leakage): models Fermi-estimate giraffe spots under a donation threshold and often drift toward the morally favored side while the CoT denies bias.

**Questions.** Why? Where do values intervene? Disclose or turn off? Can a Gilg-style linear direction predict and causally mediate?

Write-up is the Google Doc on the application form (not in this repo). This repo is code, labels, and local experiment readouts.

## Headline results

| Piece | Finding |
|-------|---------|
| Claude labels | Rescue `intentional_steer` **73%** vs controls **0%** (honest_revision 3% vs 55%) |
| All required rescues (n=102) | 52% steer / 39% mixed / 9% honest |
| Local Qwen2.5-3B | Mostly **threshold parking** (different failure mode) |
| Local Qwen3-4B | Asymmetric leakage, much less parking |
| Disclose (4B) | **FAIL** — 0/32 admits |
| `ignore_bet` (4B) | **WEAK** — MRF only nicks; below frac_good still ~0.875 |
| Gilg outcome dir (4B) | **FAIL** — LOO AUROC ~chance; no mediate win vs random |
| Revision resample (4B) | **Partial yes** — mean frac_flip **0.331** vs ~0.11 on 3B; above orig-good ~**0.86** |

Living ACH notes: [`docs/ACH.md`](docs/ACH.md). Shipped vs local bridge: [`docs/BRIDGE_SHIPPED_VS_LOCAL.md`](docs/BRIDGE_SHIPPED_VS_LOCAL.md).

## Repo map

```
labeling_packet/          Rubric + CoT samples + ben_labels.csv (102 RESCUEs + 20 Claude controls)
analysis/crossing.py      Auto rescue / MRF / gap stats on shipped trajectories
analysis/revision_taxonomy.py
analysis/option2_claude/  Extra Claude quote pack
analysis/local_qwen/      Local Donation Bet, disclose, steer, Gilg, resample (RTX 3080)
analysis/local_qwen/results_3080/   Checked readouts (JSON)
docs/                     ACH, bridge, status notes
docs/figures/             Write-up figures (PNG)
scripts/                  PowerShell / bash runners for 3080
vendor/value-leakage/     Upstream Aditya code + shipped runs (not original)
```

## Reproduce (offline)

**Phase 1 — shipped rollouts (no API):**

```bash
python analysis/crossing.py
# labels: labeling_packet/results/ben_labels.csv
# summary: analysis/ben_labels_summary.json
```

**Phase 2 — local open-weight (GPU):** see [`analysis/local_qwen/README.md`](analysis/local_qwen/README.md) and `scripts/run_*_3080.ps1`. Key checked artifacts:

- `analysis/local_qwen/results_3080/qwen3_4b_resample_readout.json`
- `analysis/local_qwen/results_3080/option1_gilg_readout.json`
- `analysis/local_qwen/results_3080/qwen3_4b_disclose_turnoff_readout.json`
- `analysis/local_qwen/results_3080/steer_sweep_readout.json`

## Hours

14h research (5h labeling/forensics + 9h local 3080) + 2h write-up (Neel’s separate write-up allowance).

## Credit

Upstream Donation Bet code/data in `vendor/value-leakage` belong to [adsingh-64/value-leakage](https://github.com/adsingh-64/value-leakage). Labels, crossing analysis, local pilots, and write-up are original.
