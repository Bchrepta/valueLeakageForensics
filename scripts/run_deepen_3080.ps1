# Deepening sweeps on RTX 3080 (items 1-2 + 4)
# IMPORTANT: use --alphas=... and --layers=... (equals form).
# PowerShell treats bare -0.4 as a switch and breaks argparse.

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = (Get-Location).Path

$Base = "analysis\local_qwen\runs\Qwen2.5-3B-Instruct_20260827_223600"
if (-not (Test-Path $Base)) {
  $Base = (Get-ChildItem analysis\local_qwen\runs | Where-Object { $_.Name -match "Qwen2.5-3B" -and $_.Name -notmatch "turnoff|disclose|smoke" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
}
Write-Host "BASE = $Base"

# --- (1)+(2) Harden + better directions on 3B ---
python -m analysis.local_qwen.steer_sweep `
  --run_dir $Base `
  --model Qwen/Qwen2.5-3B-Instruct `
  --device cuda `
  --direction outcome `
  --layers=6,12,18,24,30 `
  --alphas=-0.6,-0.4,-0.2,0,0.2 `
  --n 12 `
  --tag outcome_sweep

python -m analysis.local_qwen.steer_sweep `
  --run_dir $Base `
  --model Qwen/Qwen2.5-3B-Instruct `
  --device cuda `
  --direction parked `
  --layers=12,18,24 `
  --alphas=-0.4,0 `
  --n 12 `
  --tag parked_sweep

# --- (4) Qwen3-4B: reuse existing run if present, else sample ---
$Model4 = "Qwen/Qwen3-4B"
$Run4 = Get-ChildItem analysis\local_qwen\runs -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match "qwen3_4b|Qwen3-4B" } |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $Run4) {
  python -m analysis.local_qwen.run_donation_bet `
    --model $Model4 `
    --n 16 `
    --device cuda `
    --load_in_4bit `
    --tag qwen3_4b
  $Run4 = Get-ChildItem analysis\local_qwen\runs | Where-Object { $_.Name -match "qwen3_4b|Qwen3-4B" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}
Write-Host "RUN4 =" $Run4.FullName

python -m analysis.local_qwen.threshold_parking_audit --run_dir $Run4.FullName --out analysis\local_qwen\results_3080\parking_qwen3_4b.json

python -m analysis.local_qwen.steer_sweep `
  --run_dir $Run4.FullName `
  --model $Model4 `
  --device cuda `
  --load_in_4bit `
  --direction outcome `
  --layers=12,20,28 `
  --alphas=-0.4,0 `
  --n 10 `
  --tag qwen3_4b_outcome

Write-Host "Done. Copy sweep_summary.json into analysis/local_qwen/results_3080/"
Write-Host "Bridge: docs/BRIDGE_SHIPPED_VS_LOCAL.md"
