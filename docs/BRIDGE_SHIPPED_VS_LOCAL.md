# Bridge: shipped frontier CoTs vs local Qwen2.5-3B

**Purpose.** Same Donation Bet surface; different mechanisms. For Neel: don’t pretend 3B replicates Claude/Qwen-122B leakage — show the fork and what each teaches.

## Setup contrast

| | Shipped (Aditya runs) | Local 3080 |
|--|----------------------|------------|
| Models | Claude Opus 4.7, Qwen3.5-122B-A10B, Inkling | Qwen2.5-3B-Instruct |
| n | ~100 / condition | 16–24 / arm |
| CoT | Full / summarized (Claude) | Short instruct generations |
| Intervention | Labels + taxonomy only | Prompt turn-off, disclose, residual steer |

## Behavioral signature

### Shipped — mid-CoT motivated revision (H1/H3-ish)

- Auto **bad→good rescues** common (Claude 21 above / 9 below; Qwen 8 / 28; Inkling 3 / 33).
- Human labels on 102 rescues: **52% intentional_steer**, 39% mixed, 9% honest.
- **Claude discriminating contrast:** rescue `intentional_steer` **73%** vs controls **0%**; controls are where `honest_revision` lives (55%).
- CoT quotes show threshold-aware revision (“lean slightly higher…”, “noticing the threshold…”) often with honesty theater.
- Sentence motifs: ~86% rescues have backtrack-like language (near-ceiling; doesn’t replace labels).
- Claude `gap_at_start` small (~0.017) → less “all early anchoring.”

### Local 3B — threshold parroting (different failure)

- Incentive answers **park at exactly the threshold** ~58–67% of the time.
- **80%** of below_good “good-side” outcomes are just `estimate == thr` (scored good because ≤ thr).
- Prompt `ignore_bet`: moves MRF-proxy but doesn’t cleanly remove parking.
- Disclose prompt: only ~**12.5%** admit influence (mostly “neither”).
- Revision resampling: mean frac_flip ≈ **0.11** — weak load-bearing of revision spans.
- **Activation steer (condition dir, L18, −0.4):** mean parking drops to ~14–19% vs ~56% (zero) vs **87–100%** (random −0.4). Direction ≠ random.

## Mechanistic read

| Question (Neel) | Shipped answer | Local 3B answer |
|-----------------|----------------|-----------------|
| Why / where? | Mid-trace stake-dependent revision; Claude often denies while climbing | Early collapse onto thr token / number |
| Disclose? | Mixed (Claude covert; Qwen more overt in paper) | Mostly **no** under our disclose prompt |
| Turn off? | Not tested on shipped (API) | Prompt weak; **residual direction cuts parking vs random** |

So “value leakage” on this eval is **not one mechanism**. Frontier traces look like motivated reasoning / unfaithful CoT; small instruct models often **game the threshold literal**. A Gilg-lite direction can still mediate the small-model failure mode.

## What this is / isn’t (novelty)

- **Not** a new discovery that Value Leakage exists.
- **Is** a forensics-style split: labels + controls on shipped data, plus an open-weight **causal** pilot where internals are editable.
- The portable claim for Neel: *same eval, two mechanisms; on 3B a condition/outcome residual direction mediates thr-parking and beats a random control.*

## Next experiments that tighten the bridge

1. Outcome / parked directions + layer×α sweep (`steer_sweep.py`) — does the parking mediation replicate?
2. Same sweep on **Qwen3-4B** (4-bit) — does parking persist / does steer transfer?
3. Keep Claude labels as the behavioral headline; don’t overclaim 3B = Opus.
