# Neel Phase 2 — status after items 1–4

## Done in-repo

### 1. Sentence taxonomy (shipped RESCUEs × Ben labels) — **DONE**
- Script: `analysis/revision_taxonomy.py`
- Outputs: `analysis/revision_taxonomy_summary.json`, `revision_taxonomy_per_sample.csv`
- Headline: **86%** of labeled rescues contain a “motivated backtrack” motif (threshold/stake near revision cue).
- Important skepticism: backtrack rate is **high across all human labels** (steer 85%, mixed 88%, honest 89%) — regex motifs are near-universal in rescues; **they do not replace Ben’s labels**. Claude shows lower motif rate (53%), consistent with summarized CoTs.
- Honesty+stake co-occurrence: **94%** overall; slightly lower on `honest_revision` (78%).

### 2–4. Local Donation Bet + resampling + turn-off — **CODE READY; RUN ON YOUR 3080**
Cloud VM has **no GPU**. Pipeline is ready:

```bash
# on desktop 3080, from repo root
pip install torch transformers accelerate
bash scripts/run_local_3080.sh
# or step-by-step — see analysis/local_qwen/README.md
```

- `analysis/local_qwen/run_donation_bet.py` — baseline → threshold → above/below
- `analysis/local_qwen/resample.py` — Thought Anchors–style cuts at revision cues
- `analysis/local_qwen/run_donation_bet.py --system_prompt ignore_bet` — turn-off
- `analysis/local_qwen/compare_turnoff.py` — compare MRF-proxy

Default model: `Qwen/Qwen2.5-3B-Instruct` (3080-friendly). Smoke-tested parser + optional tiny CPU run in CI/agent if present under `runs/*smoke*`.

## What you must run locally before Neel write-up
1. `bash scripts/run_local_3080.sh` with `N=24` (or higher)
2. Confirm `summary.json` `mrf_proxy` and `resample_summary.json` `mean_frac_flip`
3. Paste those numbers into the Neel exec summary
