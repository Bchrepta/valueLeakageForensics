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

## Deepening (layer×α + better directions + Qwen3-4B)

```powershell
git pull
.\scripts\run_deepen_3080.ps1
```

Or stepwise — see script comments. Primary metric in `sweep_summary.json` → `table[].mean_frac_parked`.

Bridge writeup (offline): `docs/BRIDGE_SHIPPED_VS_LOCAL.md`

Hub ids: `Qwen/Qwen2.5-3B-Instruct` (done), `Qwen/Qwen3-4B` with `--load_in_4bit` (needs `bitsandbytes`). If Qwen3 chat adds thinking tokens, compare parked rates to 3B before over-interpreting steer.

