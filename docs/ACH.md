# ACH — Value Leakage / Donation Bet

**Core question:** When models drift giraffe-spot estimates toward the donation-favored side of a threshold, is that intentional motivated reasoning (unfaithful CoT), honest-but-failed control, anchoring, or something else?

**Primary data:** `vendor/value-leakage/runs/` (Aditya’s replications). Center models: `qwen3.5-122b-a10b`, `claude-opus-4-7`, `inkling` (high MRF).

**Metric reminder (from Aditya README):**  
- `motivated_reasoning_factor` (MRF) = drift asymmetry (above − below), not the level gap.  
- Pooled curves mix start-above / start-below — trust start-split panels.  
- Convergence to threshold alone is not motivated reasoning (baseline does it too).

---

## Hypotheses

| ID | Hypothesis | If true, we should see… | Discriminating test |
|----|------------|-------------------------|---------------------|
| **H1** | Intentional motivated reasoning (steers toward good side) | Elevated **bad→good rescues** under incentive vs baseline; CoT revises after threshold compare; admissions *or* denials while still steering | Phase 1 crossings; Phase 2 resample “revision-after-threshold” sentences |
| **H2** | Honest intent, failed control | Frequent **deny_influence** language; rescues look like ordinary uncertainty; honesty/longer-reasoning reduces bias | Compare verbal denials vs rescue rate; later: honesty prompt intervention |
| **H3** | Unfaithful theater (trained not to admit) | Denies bias while distributional bias remains; Qwen more overt than Claude on same task | Cross-model disclosure contrast on shipped CoTs |
| **H4** | Anchoring / early bias, not mid-CoT motivation | Large `gap_at_start`, low MRF / few mid-trace rescues | factor.json gap_at_start vs rescue counts |
| **H5** | Framing artifact / sycophancy, not moral values | Bias collapses under non-moral stakes (needs new samples) | Phase 2+ prompt ablation (paper E.8 already explores; we may extend) |

---

## Phase 1 provisional readout (auto stats — **[CHECK]** before trusting)

From `python analysis/crossing.py` (trajectory first vs last vs threshold):

| Model | MRF | Rescues above_good | Rescues below_good | Notes |
|-------|-----|--------------------|--------------------|-------|
| qwen3.5-122b-a10b | ~0.027 | 8 | 28 | High “admit_steer” *and* “deny” regex hits — **regex noisy; read samples** |
| claude-opus-4-7 | ~0.036 | 21 | 9 | Classic paper vibe: “honest estimate / not gaming” while moving to good side |
| inkling | ~0.063 | 3 | 33 | Highest MRF in Aditya panel; asymmetric rescues |
| deepseek-v4-pro | ~0.012 | 9 | 12 | Weaker |
| qwen3p8 | ~0.000 | 12 | 2 | Near-null MRF — useful negative control |

**Working conjecture (not a conclusion):** H1+H3 mixture — incentive conditions produce **rescues toward the good side**; Claude-style CoTs often **deny gaming** during rescues. H4 may also contribute (nontrivial `gap_at_start` on several models).

---

## Next discriminating moves

1. **[CHECK]** Human-label `analysis/check_samples/*.md` (rescue vs control).  
2. Tighten verbal taxonomy with labels from (1), re-score.  
3. Phase 2: sentence resampling on revision-after-threshold spans (outside 5h take-home clock if submitting to Aditya).  
4. Optional API: honesty / “ignore threshold” system prompts on one open model.

---

## What would falsify H1

- Rescue rate under incentive ≈ baseline regression-to-median (no asymmetry).  
- Ablating “revision-after-threshold” sentences does **not** change final-side distribution (Phase 2).  
- Models that *admit* steering show *less* bias than deniers (would favor H2/H3 story differently — still informative).
