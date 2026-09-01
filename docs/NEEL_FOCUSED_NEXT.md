# Neel deepening — focused plan (post–3080 pilot)

## Active plan (reset-clock Option 1 → maybe 2)

| Step | Goal | Command / doc |
|------|------|----------------|
| **1. Gilg predict+mediate** | On **Qwen3-4B** (real asymmetry, low parking): LOO AUROC for outcome direction + steer vs random with **`mean_frac_good` primary** | `scripts/run_option1_gilg_3080.ps1` / `analysis.local_qwen.gilg_mediate` |
| **2. Claude forensics** | Only after 1: is `intentional_steer` revision load-bearing? | `docs/OPTION2_FORENSICS.md` |
| **3. Write-up** | ≤600-word exec summary + form Qs | after 1 (and 2 if time) |

Keep local runs on disk:
- `analysis/local_qwen/runs/Qwen2.5-3B-Instruct_20260827_223600`
- `analysis/local_qwen/runs/Qwen2.5-3B-Instruct_20260827_231952_turnoff`
- `analysis/local_qwen/runs/Qwen3-4B_20260828_004946_qwen3_4b`

## What Neel literally asked (Value Leakage)

> why? Where do the values intervene? Can you make it disclose, or **turn the effect off**? Can you combine it with **Gilg et al** to find a **linear direction** predicting it and **causally mediating** it?

So “turn off” is **not only** a system prompt. Hierarchy:

| Level | Method | Status for us |
|-------|--------|----------------|
| A. Behavioral | `ignore_bet` / honesty / disclose prompts | A done (messy); disclose weak on 3B |
| B. Activation steering | Contrastive **linear direction** in residual stream; add/subtract to reduce good-side bias | **Option 1 now** on 4B (predict + mediate) |
| C. Single-neuron edit | Sparse neurons for “good cause” | Related lore; **not** what he named — skip unless B works |

Gilg et al. ≈ preference / evaluative **vector** (probe + steer), not classical “find one neuron.” Your memory of turning features up/down is the right *idea*; the modern object is a **direction**, often at residual stream / last user token.

## Do more — but only these (ranked)

### P0 — Option 1 (Gilg on 4B)
1. Confirm 4B still shows below_good asymmetry with low parking (already: frac_good ~0.94 below, parked ~25%).
2. **Predict:** LOO mean-diff probe AUROC at last assistant token across layers (`--exclude_parked`).
3. **Causal:** steer −α·d vs 0 vs random; primary = **mean_frac_good** / mrf_proxy (parking secondary).

### P1 — Option 2 if Option 1 lands
4. Claude denial/theater + random quotes + sentence resample on labeled rescues.

### Do not
- More 3B α×layer parking sweeps  
- Full SAE / J-lens before a working probe  
- Selling parking mediation as “turned off values”

## Narrative for the app
1. Shipped Claude: rescue↔control labels (behavioral headline).  
2. Local: 3B = thr-parking organism; 4B = better leakage organism.  
3. Gilg-lite on 4B: predict AUROC + causal mediate (success *or* clean failure + random).  
4. Optional: Claude load-bearing resample.
