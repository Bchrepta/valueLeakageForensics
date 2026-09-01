# P0 on RTX 3080 (PowerShell) — run from repo root with venv active
# Prerequisites: git pull users/bchrepta/neel-offline-phase2-7426

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = (Get-Location).Path
$Model = "Qwen/Qwen2.5-3B-Instruct"
$N = 24

# Locate base + turnoff runs
$Base = Get-ChildItem analysis\local_qwen\runs | Where-Object { $_.Name -eq "Qwen2.5-3B-Instruct_20260827_223600" }
if (-not $Base) { $Base = Get-ChildItem analysis\local_qwen\runs | Where-Object { $_.Name -notmatch "turnoff|smoke" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1 }
$Turnoff = Get-ChildItem analysis\local_qwen\runs | Where-Object { $_.Name -match "turnoff" -and $_.Name -notmatch "smoke" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1

Write-Host "BASE =" $Base.FullName
Write-Host "TURNOFF =" $Turnoff.FullName

# P0a — threshold parking
python -m analysis.local_qwen.threshold_parking_audit --run_dir $Base.FullName --run_dir $Turnoff.FullName --out analysis\local_qwen\results_3080\threshold_parking_3080.json

# P0c — disclose prompt (same threshold)
$Thr = (Get-Content (Join-Path $Base.FullName "threshold.json") | ConvertFrom-Json).threshold
python -m analysis.local_qwen.run_donation_bet --model $Model --n $N --device cuda --system_prompt disclose --tag disclose --threshold $Thr
$Disc = Get-ChildItem analysis\local_qwen\runs | Where-Object { $_.Name -match "disclose" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
python -m analysis.local_qwen.score_disclose --run_dir $Disc.FullName

# P0b — Gilg-lite activation steer (mid layer; ±alpha + random control)
# n=16 keeps wall-clock reasonable; bump to 24 if you have time
python -m analysis.local_qwen.steer_turnoff --run_dir $Base.FullName --model $Model --device cuda --n 16 --alpha 0.4 --collect_n 1

Write-Host "P0 done. Check:"
Write-Host "  analysis/local_qwen/results_3080/threshold_parking_3080.json"
Write-Host "  $($Disc.FullName)\disclose_score.json"
Write-Host "  $($Base.FullName)\steer_layer*\steer_summary.json"
