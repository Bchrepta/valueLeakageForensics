# Local Qwen Donation Bet (RTX 3080, no OpenRouter)

## What this is
Phase-2 style experiments Neel wants on Value Leakage, runnable offline:
1. Reproduce Donation Bet on a small Qwen that fits a 3080
2. Thought Anchors–style **resampling** at revision cuts
3. **Turn-off** via `ignore_bet` system prompt

Cloud agents have no GPU — run these on your desktop 3080.

## Setup (3080)
```bash
cd /path/to/valueLeakageForensics
python -m venv .venv && source .venv/bin/activate
pip install 'torch' 'transformers>=4.44' accelerate sentencepiece protobuf
# optional 4-bit:
pip install bitsandbytes
```

Recommended model (fits 10GB comfortably): `Qwen/Qwen2.5-3B-Instruct`  
Alt: `Qwen/Qwen3-4B` if you prefer Neel's Qwen3.x defaults (may want `--load_in_4bit`).

## Commands
```bash
# Donation bet (baseline + above_good + below_good)
python -m analysis.local_qwen.run_donation_bet \
  --model Qwen/Qwen2.5-3B-Instruct --n 24 --device cuda

# Turn-off intervention (same n; compare mrf_proxy to above)
python -m analysis.local_qwen.run_donation_bet \
  --model Qwen/Qwen2.5-3B-Instruct --n 24 --device cuda \
  --system_prompt ignore_bet --tag turnoff

# Resample revision spans from a finished run
python -m analysis.local_qwen.resample \
  --run_dir analysis/local_qwen/runs/<stamp> --k 8 --device cuda
```

Outputs land in `analysis/local_qwen/runs/<model>_<stamp>/`:
- `summary.json` — medians, frac on good side, `mrf_proxy`
- `resample_summary.json` — frac_flip when regenerating after revision cut
- `*.json` rollouts with full text

## Option 1 — Gilg predict + mediate (Qwen3-4B) **← run this next**

Neel’s Value Leakage ask: direction that **predicts** and **causally mediates**.
Primary causal metric = **mean frac_good** (not parked%).

```powershell
git pull
.\scripts\run_option1_gilg_3080.ps1
```

Or stepwise:

```powershell
$env:PYTHONPATH = (Get-Location).Path
$Run4 = "...\analysis\local_qwen\runs\Qwen3-4B_20260828_004946_qwen3_4b"

python -m analysis.local_qwen.gilg_mediate `
  --run_dir $Run4 `
  --model Qwen/Qwen3-4B --device cuda --load_in_4bit `
  --layers=8,12,16,20,24,28 `
  --alphas=-0.4,-0.2,0 `
  --n 16 --exclude_parked --tag option1_gilg
```

Outputs: `gilg_mediate_option1_gilg/predict_summary.json` + `mediate_summary.json`.  
Success: LOO AUROC ≫ 0.5; `steer_-0.4` lowers `mean_frac_good` vs zero **and** vs random.

After that → Option 2 Claude forensics: `docs/OPTION2_FORENSICS.md`.

## Deepening (older layer×α parking sweeps)

```powershell
git pull
.\scripts\run_deepen_3080.ps1
```

Or stepwise — see script comments. Primary metric in older `sweep_summary.json` → `table[].mean_frac_parked`.

Bridge writeup (offline): `docs/BRIDGE_SHIPPED_VS_LOCAL.md`

Hub ids: `Qwen/Qwen2.5-3B-Instruct` (done), `Qwen/Qwen3-4B` with `--load_in_4bit` (needs `bitsandbytes`). If Qwen3 chat adds thinking tokens, compare parked rates to 3B before over-interpreting steer.

