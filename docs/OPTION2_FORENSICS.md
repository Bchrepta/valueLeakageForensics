# Option 2 — Claude rescue forensics (after Option 1)

Option 1 on Qwen3-4B is done: **predict AUROC ~ chance; causal steer wrong-way**. Pivot here.

## Question
On Claude rescues labeled `intentional_steer`, is the mid-CoT revision **load-bearing**, or honesty-theater (H1 vs H3)?

## Offline pack (no GPU / no API) — run now

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m analysis.option2_claude_forensics --seed 0 --n_quotes 10
```

Writes:
- `analysis/option2_claude/forensics_summary.json` — rates by group
- `analysis/option2_claude/forensics_quotes.md` — **random** quotes for the Neel doc

Human label contrast remains the headline (Claude rescue `intentional_steer` 73% vs controls 0%). Regex theater flags are secondary (Claude summaries almost always talk about honesty).

## Optional causal half (API)
Sentence resample / prefix regenerate on revision cuts (Nebius / OpenRouter). Only if hours remain after quotes are in the draft.

## Success for Neel
One clear story: Claude mid-CoT steer with random quotes + rescue↔control contrast; local Gilg on 4B as honest null; 3B parking as different organism.
