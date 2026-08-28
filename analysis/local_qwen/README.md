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

## P0 (Neel deepening)
```powershell
git pull
.\scripts\run_p0_3080.ps1
```
Does: threshold-parking audit, **disclose** prompt run + score, **Gilg-lite activation steering** turn-off (`steer_turnoff.py`).

Manual pieces:
```powershell
python -m analysis.local_qwen.threshold_parking_audit --run_dir <base> --run_dir <turnoff> --out analysis\local_qwen\results_3080\threshold_parking_3080.json
python -m analysis.local_qwen.run_donation_bet --model Qwen/Qwen2.5-3B-Instruct --n 24 --device cuda --system_prompt disclose --tag disclose --threshold 15000000
python -m analysis.local_qwen.score_disclose --run_dir <disclose_run>
python -m analysis.local_qwen.steer_turnoff --run_dir <base> --model Qwen/Qwen2.5-3B-Instruct --device cuda --n 16 --alpha 0.4
```

## Notes / limitations
- No Claude estimate/trajectory judges — regex parsing (document this for Neel).
- Small models may show weaker leakage than Qwen 122B; a null result is still informative.
- `--n 24` is a pilot; bump to 40–50 if time allows.
- 3B incentive answers often **park at exactly the threshold** — always report `frac_parked` beside MRF-proxy.
