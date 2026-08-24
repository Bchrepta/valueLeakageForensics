# valueleakageforensics

SPAR / model-forensics deep dive into **Value Leakage** (Donation Bet): why models drift Fermi estimates toward morally favored outcomes, and whether that looks like intentional motivated reasoning vs failed honesty / unfaithful CoT.

**Mentor framing:** Aditya Singh (SPAR) — [Concrete Problems in Model Forensics](https://docs.google.com/document/d/1v6bv3JQLrfdI7Mh_kVivm-Th1omm7Dw7ddTG-WQruLc). Also on-menu for Neel Nanda MATS (Science of Model Character).

## Status

Phase 1 (this branch): offline analysis of Aditya's shipped rollouts — no API keys required.

## Quick start

```bash
# already vendored:
#   vendor/value-leakage/   (adsingh-64/value-leakage + runs/)

python analysis/crossing.py
# open docs/ACH.md and analysis/check_samples/*.md
```

Regenerate Aditya's trajectory plots (optional):

```bash
cd vendor/value-leakage && uv sync
uv run python -m value_leakage.plot --run_dir runs/qwen3.5-122b-a10b_20260815_030702
```

## Layout

```
docs/ACH.md           competing hypotheses + predictions
docs/HANDOFF.md       context for continuing on another machine
docs/CHECKLIST.md     what Ben must manually verify  [CHECK]
analysis/crossing.py  trajectory side-crossing stats
analysis/check_samples/  random CoT excerpts for human review
vendor/value-leakage/ Aditya's minimal repro + shipped runs
```

## Target claim (Phase 1 → 2)

**H1:** “motivated backtracking” sentences that appear after landing on the *bad* side of the threshold are **load-bearing** for bias.  
Phase 1: measure how often traces **rescue** bad→good under incentive, and how CoTs talk about honesty vs steering.  
Phase 2 (later, API): sentence resampling / ablation on those sentences (Thought Anchors–style).

## License / attribution

Shipped data and experiment code in `vendor/value-leakage` belong to [adsingh-64/value-leakage](https://github.com/adsingh-64/value-leakage) (Value Leakage paper / TruthfulAI). Our analysis code is original to this repo.
