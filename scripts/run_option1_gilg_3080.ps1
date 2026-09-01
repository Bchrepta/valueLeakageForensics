# Option 1 - Gilg predict + mediate on Qwen3-4B (RTX 3080)
# Neel: linear direction that PREDICTS and CAUSALLY MEDIATES value leakage.
# Primary causal metric: mean frac_good (not parked%).
#
# PowerShell: always use --alphas=... and --layers=... (equals form).

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = (Get-Location).Path

$Model4 = "Qwen/Qwen3-4B"
$Run4 = Get-ChildItem analysis\local_qwen\runs -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match "qwen3_4b|Qwen3-4B" -and $_.Name -notmatch "smoke|turnoff|disclose" } |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $Run4) {
  Write-Host "No Qwen3-4B run found - sampling donation bet n=24 ..."
  python -m analysis.local_qwen.run_donation_bet `
    --model $Model4 `
    --n 24 `
    --device cuda `
    --load_in_4bit `
    --tag qwen3_4b
  $Run4 = Get-ChildItem analysis\local_qwen\runs |
    Where-Object { $_.Name -match "qwen3_4b|Qwen3-4B" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
}

Write-Host "RUN4 =" $Run4.FullName

# Optional: enlarge bank if existing run is small (skip if you already have n>=16)
# python -m analysis.local_qwen.run_donation_bet --model $Model4 --n 24 --device cuda --load_in_4bit --tag qwen3_4b_n24

python -m analysis.local_qwen.threshold_parking_audit `
  --run_dir $Run4.FullName `
  --out analysis\local_qwen\results_3080\parking_qwen3_4b.json

# Predict LOO AUROC across layers + causal mediate on top-2 layers
python -m analysis.local_qwen.gilg_mediate `
  --run_dir $Run4.FullName `
  --model $Model4 `
  --device cuda `
  --load_in_4bit `
  --layers=8,12,16,20,24,28 `
  --alphas=-0.4,-0.2,0 `
  --n 16 `
  --exclude_parked `
  --tag option1_gilg

Write-Host ""
Write-Host "Done. Copy:"
Write-Host ("  {0}\gilg_mediate_option1_gilg\predict_summary.json" -f $Run4.FullName)
Write-Host ("  {0}\gilg_mediate_option1_gilg\mediate_summary.json" -f $Run4.FullName)
Write-Host "into analysis\local_qwen\results_3080\ and paste tables back to the agent."
Write-Host ""
Write-Host "Success rule: outcome LOO AUROC >> 0.5; steer -alpha lowers mean_frac_good vs zero AND vs random."
Write-Host "After Option 1: Option 2 = Claude rescue sentence-resample (see docs/OPTION2_FORENSICS.md)."
