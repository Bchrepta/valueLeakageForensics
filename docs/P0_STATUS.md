# P0 status

## P0a — Threshold parking — DONE (from your console numbers)

| Run | Condition | % at exactly 15M | % good side | Of goods, % that are parked |
|-----|-----------|------------------|-------------|------------------------------|
| base | above_good | **58%** | 21% | 0% (parked ⇒ bad when above needs >thr) |
| base | below_good | **67%** | 83% | **80%** |
| turnoff | above_good | 71% | 13% | 0% |
| turnoff | below_good | 46% | 67% | 69% |

**Takeaway:** Most of the below_good “success” is threshold parroting, not mid-CoT steer like Claude.

File: `analysis/local_qwen/results_3080/threshold_parking_from_console.json`

## P0b — Activation steer — CODE READY (run on 3080)

```powershell
$env:PYTHONPATH = (Get-Location).Path
git pull
$Base = "analysis\local_qwen\runs\Qwen2.5-3B-Instruct_20260827_223600"
python -m analysis.local_qwen.steer_turnoff --run_dir $Base --model Qwen/Qwen2.5-3B-Instruct --device cuda --n 16 --alpha 0.4 --collect_n 1
```

Output: `$Base\steer_layer*\steer_summary.json` (steer ±α, zero, random control).

## P0c — Disclose — CODE READY (run on 3080)

```powershell
$Thr = 15000000
python -m analysis.local_qwen.run_donation_bet --model Qwen/Qwen2.5-3B-Instruct --n 24 --device cuda --system_prompt disclose --tag disclose --threshold $Thr
$Disc = Get-ChildItem analysis\local_qwen\runs | Where-Object { $_.Name -match "disclose" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
python -m analysis.local_qwen.score_disclose --run_dir $Disc.FullName
```

Or all remaining GPU P0: `.\scripts\run_p0_3080.ps1`
