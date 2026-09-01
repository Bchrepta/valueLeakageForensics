#!/usr/bin/env bash
# Run on desktop RTX 3080 (from repo root, venv activated).
set -euo pipefail
MODEL="${MODEL:-Qwen/Qwen2.5-3B-Instruct}"
N="${N:-24}"
DEVICE="${DEVICE:-cuda}"
EXTRA=()
if [[ "${LOAD_4BIT:-0}" == "1" ]]; then EXTRA+=(--load_in_4bit); fi

echo "== Donation bet =="
python -m analysis.local_qwen.run_donation_bet \
  --model "$MODEL" --n "$N" --device "$DEVICE" "${EXTRA[@]}"

# pick newest run dir for this model stem
RUN=$(ls -dt analysis/local_qwen/runs/* | head -1)
echo "Using RUN=$RUN"

echo "== Resample =="
python -m analysis.local_qwen.resample \
  --run_dir "$RUN" --k "${K:-8}" --device "$DEVICE" "${EXTRA[@]}"

THR=$(python -c "import json;print(json.load(open('$RUN/threshold.json'))['threshold'])")
echo "== Turn-off (ignore_bet), fixed threshold=$THR =="
python -m analysis.local_qwen.run_donation_bet \
  --model "$MODEL" --n "$N" --device "$DEVICE" "${EXTRA[@]}" \
  --system_prompt ignore_bet --tag turnoff --threshold "$THR"

echo "Done. Compare summary.json mrf_proxy between $RUN and the *_turnoff run."
