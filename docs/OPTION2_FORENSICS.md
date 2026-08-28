# Option 2 — Claude rescue forensics (after Option 1)

**Do this only after** Qwen3-4B Gilg predict+mediate (`scripts/run_option1_gilg_3080.ps1`) finishes and you have numbers.

## Question
On Claude rescues labeled `intentional_steer`, is the mid-CoT revision **load-bearing**, or theater (H1 vs H3)?

## Cheap stack (no GPU / no OpenRouter required for the labeling half)

1. **Random quotes** — sample 10 `intentional_steer` + 10 control CoTs from `labeling_packet/`; paste into Neel doc (he requires random examples if labels are load-bearing).
2. **Denial/theater flag** — score whether honesty talk co-occurs with climbing (H3).
3. **Sentence resample** — if you have API access (Nebius / OpenRouter): cut at revision motif, regenerate k=8, measure frac_flip of final side vs control cuts on non-rescue spans.

## Success for Neel
One decisive causal claim on shipped Claude (or honest failure + controls), not another 3B sweep.

Repo hooks (existing): `analysis/revision_taxonomy.py`, `analysis/local_qwen/resample.py` (local models). Claude API resample is a small new script once Option 1 is in.
