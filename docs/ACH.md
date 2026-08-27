# ACH — Value Leakage / Donation Bet

**Question.** When giraffe-spot estimates drift toward the donation-favored side of a threshold, is that intentional motivated reasoning, honest-but-failed control, unfaithful CoT, early anchoring, or framing?

**Data.** `vendor/value-leakage/runs/` (Aditya’s replications). Focus: `qwen3.5-122b-a10b`, `claude-opus-4-7`, `inkling`.

**Metrics (Aditya README).** MRF = drift asymmetry (above − below), not the level gap. Threshold convergence alone is not motivated reasoning (baseline does it too). Prefer start-split panels over pooled curves.

## Hypotheses

| ID | Hypothesis | If true… | Test |
|----|------------|----------|------|
| H1 | Intentional motivated reasoning | Bad→good rescues; stake-dependent revisions after threshold compare | Crossing counts; CoT labels; later sentence resampling |
| H2 | Honest intent, failed control | Rescues look like ordinary Fermi revision | Label distribution; honesty-prompt intervention |
| H3 | Unfaithful theater | Denies bias while still steering | Cross-model CoT read (esp. Claude) |
| H4 | Early anchoring | Large `gap_at_start`; little mid-trace rescue | `factor.json` vs rescue counts |
| H5 | Framing / sycophancy | Bias drops under non-moral stakes | New prompts (untested) |

## Auto crossings

From `analysis/crossing.py` (traj first vs last vs threshold):

| Model | MRF | Rescues above | Rescues below |
|-------|-----|---------------|---------------|
| inkling | 0.063 | 3 | 33 |
| claude-opus-4-7 | 0.036 | 21 | 9 |
| qwen3.5-122b-a10b | 0.027 | 8 | 28 |
| deepseek-v4-pro | 0.012 | 9 | 12 |
| qwen3p8 | ~0 | 12 | 2 |

Regex admit/deny flags in `crossing.py` are noisy — not used for claims.

## Human labels (Ben Chrepta, 2026-08-24)

Source: `labeling_packet/results/ben_labels.csv`. Rubric: `labeling_packet/02_RUBRIC.md`.

Covered: 102/102 required RESCUEs + 20/20 Claude controls. Qwen/Inkling controls (40) unlabeled.  
QC: `traj_ok=yes` on 121/122; one `unsure` (`claude-opus-4-7__below_good__RESCUE__i61`); one `mislabeled_is_rescue` (`…CONTROL_stay_good__i16`).

### Required RESCUEs (n=102)

| Label | n | % |
|-------|---|---|
| intentional_steer | 53 | 52% |
| mixed | 40 | 39% |
| honest_revision | 9 | 9% |

| Model | n | intentional_steer | mixed | honest_revision |
|-------|---|-------------------|-------|-----------------|
| claude-opus-4-7 | 30 | 22 (73%) | 7 | 1 |
| inkling | 36 | 18 (50%) | 15 | 3 |
| qwen3.5-122b-a10b | 36 | 13 (36%) | 18 (50%) | 5 |

Inkling’s 3 above_good rescues were all `honest_revision`; its below_good rescues were steer/mixed.

### Claude controls vs rescues

| Bucket | n | intentional_steer | mixed | honest_revision | mislabeled_is_rescue |
|--------|---|-------------------|-------|-----------------|----------------------|
| RESCUE | 30 | 22 (73%) | 7 | 1 | — |
| CONTROL stay_bad | 10 | 0 | 5 | 5 | 0 |
| CONTROL stay_good | 10 | 0 | 3 | 6 | 1 |

`intentional_steer`: 73% rescues vs **0%** controls. `honest_revision`: 3% rescues vs 55% controls.  
One control was a traj miss (CoT crossed; first=last stayed at threshold). Controls still get `mixed` from threshold talk without a successful rescue.

### `gap_at_start` (H4)

| Model | MRF | gap_at_start | gap_at_end |
|-------|-----|--------------|------------|
| claude-opus-4-7 | 0.036 | 0.017 | 0.23 |
| qwen3.5-122b-a10b | 0.027 | 0.12 | 0.15 |
| inkling | 0.063 | 0.16 | 0.07 |

Claude’s early gap is small; Qwen/Inkling leave more room for early anchoring alongside mid-trace steering.

## Stance

| ID | Status | Why |
|----|--------|-----|
| H1 | Supported (provisional) | Rescues mostly steer/mixed; Claude control contrast is sharp |
| H2 | Weak as primary account | Honest revision concentrated in controls, not rescues |
| H3 | Open / plausible for Claude | Honesty talk often co-occurs with steer labels; no separate denial score |
| H4 | Open | Claude unlikely “all early”; Qwen/Inkling unresolved |
| H5 | Untested | — |

Not shown: causal load-bearing of revision-after-threshold sentences (needs resampling).

**Caveats.** Single rater; large `mixed` share (39%); Claude CoTs may be API summaries; Qwen/Inkling controls unlabeled.

## Next

1. Sentence resampling on revision-after-threshold spans (Qwen 122B / Claude).
2. Optional: label remaining controls; honesty / ignore-threshold prompts; non-moral stakes (H5).

## Falsifiers for H1

- Incentive rescue rate ≈ baseline regression-to-median.
- Resampling ablation doesn’t move final-side distribution.
- Second rater (or remaining controls) collapses the rescue↔control `intentional_steer` gap.
