# HANDOFF — continue this project elsewhere (Desktop Cursor, etc.)

## Repo

- GitHub: `bchrepta/valueleakageforensics`
- Branch used for setup: `users/bchrepta/value-leakage-forensics-setup-7426` (or whatever is current)

## Open these first

1. `docs/ACH.md` — hypotheses + **Ben’s 8/24 human labels folded in**  
2. `docs/CHECKLIST.md` — remaining [CHECK]s  
3. `labeling_packet/results/ben_labels.csv` — filled required RESCUEs  
4. `analysis/ben_labels_summary.json` — quick counts  
5. `README.md`

## Status (2026-08-25)

- Phase 1 auto crossings: done  
- Human labels on **102/102 required RESCUEs**: done  
- Claude recommended controls **20/20**: done (rescue↔control contrast strengthens H1)  
- Qwen/Inkling controls: still blank (optional)  
- Phase 2 resampling / SPAR Google Doc: **draft ready** → `docs/SPAR_TAKEHOME_DRAFT.md` (Ben: rewrite voice + paste quotes)

## Data location

`vendor/value-leakage/` = clone of https://github.com/adsingh-64/value-leakage (code + shipped `runs/`).

Raw CoTs: `runs/<model>/above_good.json` → `rows[*].reasoning`  
Trajectories: `runs/<model>/trajectories.json`  
MRF: `runs/<model>/factor.json`

**Note:** `estimates.json` in the shipped runs currently only contains `baseline` keys. For finals under incentive conditions, use **last trajectory point** (or re-judge later).

## Commands

```bash
python analysis/crossing.py
```

Optional plots:

```bash
cd vendor/value-leakage && uv sync
uv run python -m value_leakage.plot --run_dir runs/qwen3.5-122b-a10b_20260815_030702
```

## Do not do yet

- Full Google Doc write-up / SPAR email  
- Sentence resampling (parked Phase 2)  
- J-lens on 122B (needs big remote GPU / paid infra)  
- Treat regex verbal flags as ground truth without **[CHECK]**

## Target result

Show (or falsify) that **bad→good rescues** under donation incentives are the behavioral signature of motivated reasoning, and that Claude-like **honesty claims** co-occur with those rescues (unfaithful or failed introspect — TBD by Phase 2).
