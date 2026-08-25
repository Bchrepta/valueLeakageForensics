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

## Phase 1 provisional readout (auto stats)

From `python analysis/crossing.py` (trajectory first vs last vs threshold):

| Model | MRF | Rescues above_good | Rescues below_good | Notes |
|-------|-----|--------------------|--------------------|-------|
| qwen3.5-122b-a10b | ~0.027 | 8 | 28 | High “admit_steer” *and* “deny” regex hits — **regex noisy; ignore for claims** |
| claude-opus-4-7 | ~0.036 | 21 | 9 | Classic paper vibe: “honest estimate / not gaming” while moving to good side |
| inkling | ~0.063 | 3 | 33 | Highest MRF in Aditya panel; asymmetric rescues |
| deepseek-v4-pro | ~0.012 | 9 | 12 | Weaker |
| qwen3p8 | ~0.000 | 12 | 2 | Near-null MRF — useful negative control |

---

## Phase 1 human labels (Ben Chrepta, 2026-08-24)

**Source:** `labeling_packet/results/ben_labels.csv` (also `analysis/ben_labels_summary.json`).  
**Coverage:** **102/102** `priority=required` RESCUE rows. Recommended controls (60) still unlabeled.  
**Rubric:** `intentional_steer` / `mixed` / `honest_revision` / `unclear` / `mislabeled_*` (see `labeling_packet/02_RUBRIC.md`).  
**QC:** `traj_ok=yes` on 101/102; one `unsure` (`claude-opus-4-7__below_good__RESCUE__i61`). No `mislabeled_not_rescue`. Confidence: 62 high / 40 medium / 0 low.

### Overall (all required RESCUEs)

| Label | n | % |
|-------|---|---|
| `intentional_steer` | 53 | 52.0% |
| `mixed` | 40 | 39.2% |
| `honest_revision` | 9 | 8.8% |

Steer-involved (`intentional_steer` + `mixed`) = **91.2%** of auto-rescues. Pure honest revision is rare.

### By model

| Model | n | intentional_steer | mixed | honest_revision | Notes |
|-------|---|-------------------|-------|-----------------|-------|
| claude-opus-4-7 | 30 | **22 (73%)** | 7 (23%) | 1 (3%) | Strongest steer read; matches “deny while climbing” vibe |
| inkling | 36 | 18 (50%) | 15 (42%) | 3 (8%) | All 3 above_good rescues = honest_revision; below_good is steer/mixed |
| qwen3.5-122b-a10b | 36 | 13 (36%) | **18 (50%)** | 5 (14%) | Most often `mixed` — genuine Fermi + threshold pressure |

### By model × condition (rescue counts)

| Cell | n | intentional_steer | mixed | honest_revision |
|------|---|-------------------|-------|-----------------|
| Claude above_good | 21 | 16 | 4 | 1 |
| Claude below_good | 9 | 6 | 3 | 0 |
| Qwen above_good | 8 | 3 | 3 | 2 |
| Qwen below_good | 28 | 10 | 15 | 3 |
| Inkling above_good | 3 | 0 | 0 | **3** |
| Inkling below_good | 33 | 18 | 15 | 0 |

---

## Updated ACH stance (post-labels)

| ID | Status after labels | Why |
|----|---------------------|-----|
| **H1** | **Supported (provisional)** | Majority of auto-rescues read as intentional steer; Claude 73% steer. Pure honest rescues are ~9%. |
| **H2** | **Weakened as primary story** | If most rescues were honest failed control, we’d expect more `honest_revision`. Still possible for the 9 honest cases + parts of `mixed`. |
| **H3** | **Plausible co-story (esp. Claude)** | Labels don’t score “denial” as a separate field, but Claude notes often cite honesty talk while steering — consistent with unfaithful/theater overlay on H1. Needs a denial flag pass or Phase 2. |
| **H4** | **Open** | Labels are mid-trace motivation judgments; do not resolve early anchoring. Still check `gap_at_start` in `factor.json`. |
| **H5** | **Untested** | Needs non-moral stakes / new prompts. |

**Working claim (write carefully):** Among shipped **bad→good rescues**, human judgment finds **threshold-dependent steering** much more often than pure Fermi revision — especially Claude. Qwen is more often **mixed**. This supports H1 over H2 as the *dominant* rescue mechanism; it does **not** yet prove load-bearing causality (that needs Phase 2 resampling) or rule out H4 contribution to the start of the trace.

**Caveats:** Single reviewer; no control labels yet (selection on auto-RESCUE); Claude CoTs may be API summaries; `mixed` is large (39%) — don’t overclaim purity of “steer.”

---

## Next discriminating moves

1. ~~Human-label required RESCUEs~~ **Done** (Ben, 8/24/26).  
2. **Optional:** label recommended controls (≥ Claude stay_bad/stay_good) — checks auto-bucket false positives/negatives.  
3. **[CHECK]** Glance `factor.json` `gap_at_start` for H4 (Claude / Qwen / Inkling).  
4. Fold a few **random** labeled excerpts into SPAR draft (not only steer exemplars).  
5. Phase 2 (outside strict 5h if needed): Thought Anchors–style resampling on revision-after-threshold spans.  
6. Optional API: honesty / “ignore threshold” system prompts on one open model.

---

## What would falsify H1

- Rescue rate under incentive ≈ baseline regression-to-median (no asymmetry).  
- Ablating “revision-after-threshold” sentences does **not** change final-side distribution (Phase 2).  
- Human labels flip: most rescues become `honest_revision` / `mislabeled_not_rescue` under a second rater or controls show similar “steer” rates without crossing.  
- Models that *admit* steering show *less* bias than deniers (would favor H2/H3 story differently — still informative).
