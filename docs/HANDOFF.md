# HANDOFF — continue this project elsewhere (Desktop Cursor, etc.)

## Repo

- GitHub: `bchrepta/valueleakageforensics`
- Branch used for setup: `users/bchrepta/value-leakage-forensics-setup-7426` (or whatever is current)

## Open these first

1. `docs/ACH.md` — hypotheses  
2. `docs/CHECKLIST.md` — what Ben must verify  
3. `analysis/check_samples/claude-opus-4-7.md` — start human review here (clearest “deny while steering” vibe)  
4. `analysis/check_samples/qwen3.5-122b-a10b.md`  
5. `README.md`

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
