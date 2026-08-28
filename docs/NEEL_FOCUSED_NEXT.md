# Neel deepening — focused plan (post–3080 pilot)

Keep local runs on disk:
- `analysis/local_qwen/runs/Qwen2.5-3B-Instruct_20260827_223600`
- `analysis/local_qwen/runs/Qwen2.5-3B-Instruct_20260827_231952_turnoff`

Copy `summary.json`, `resample_summary.json`, `turnoff_compare.json`, `threshold.json`, `config.json` into
`analysis/local_qwen/results_3080/` for the repo (full texts can stay local / gitignored).

## What Neel literally asked (Value Leakage)

> why? Where do the values intervene? Can you make it disclose, or **turn the effect off**? Can you combine it with **Gilg et al** to find a **linear direction** predicting it and **causally mediating** it?

So “turn off” is **not only** a system prompt. Hierarchy:

| Level | Method | Status for us |
|-------|--------|----------------|
| A. Behavioral | `ignore_bet` / honesty / disclose prompts | A done (messy); disclose not done |
| B. Activation steering | Contrastive **linear direction** in residual stream; add/subtract to reduce good-side bias | **Next high-value** (Gilg-shaped; fits 3080 on 3B/4B) |
| C. Single-neuron edit | Sparse neurons for “good cause” | Related lore; **not** what he named — skip unless B works |

Gilg et al. ≈ preference / evaluative **vector** (probe + steer), not classical “find one neuron.” Your memory of turning features up/down is the right *idea*; the modern object is a **direction**, often at residual stream / last user token.

## Do more — but only these (ranked)

Each item maps to a hypothesis. Stop when clock says write.

### P0 — Must for a deeper Neel app
1. **Threshold-parking audit** on the 3080 runs (`% estimate == thr` by condition). Explains the MRF-proxy confound; 30 min.
2. **Activation “turn-off” (Gilg-lite) on Qwen2.5-3B**  
   - Collect residual-stream acts at last user token for `above_good` vs `below_good` (same threshold).  
   - Direction \(d = \mu_{above} - \mu_{below}\) (or good-side vs bad-side finals).  
   - Steer \(-\alpha d\) during generation; measure frac_good / MRF-proxy vs random-direction control.  
   - Tests: **H1 causal mediation** + Neel’s “turn off” / Gilg ask.
3. **Disclose prompt** (`--system_prompt disclose`) n=24 — Neel’s other half of “disclose or turn off.”

### P1 — If P0 fits and hours remain
4. **Claude denial/theater flag** on 30 labeled rescues (H3) — no GPU.
5. **Stricter resample** only on traces that *leave* the threshold (not parked at 15M) — cleaner H1 load-bearing test.
6. **Label 20 Qwen controls** (not all 40) — cross-model rescue↔control.

### P2 — Stretch / only if P0–P1 done
7. Same steering recipe on **Qwen3-4B** (4-bit) if 3B direction is real.
8. H5 non-moral stakes (one ablation).
9. OpenRouter / 122B — out of scope unless P0 is strong.

## Do not do (unfocused)
- More ACH rows without a new test  
- Full SAE / J-lens / neuron hunt before a working direction  
- Re-running n=100 on 3B without fixing threshold-equality analysis  
- Random prompt zoo unrelated to H1–H3 / Neel’s three questions  

## Narrative for the app if time dies after P0
1. Shipped Claude: rescue↔control labels (main behavioral claim).  
2. Local 3B: prompt turn-off moved proxy but threshold-parking confounds.  
3. Activation steering: attempt to **mechanistically** turn off (success *or* clean failure + random baseline both teach Neel something).
