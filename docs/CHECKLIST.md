# CHECKLIST — Ben must verify

Anything marked **[CHECK]** is load-bearing. Do not trust agent regex / summaries alone.

## Must do before claiming results

- [ ] **[CHECK]** Read ≥10 random **RESCUE** CoTs in `analysis/check_samples/claude-opus-4-7.md`  
      Decide per sample: intentional steer / honest revision / unclear.
- [ ] **[CHECK]** Same for `qwen3.5-122b-a10b.md` and `inkling.md` (≥5 each is OK for a first pass).
- [ ] **[CHECK]** Read ≥5 **CONTROL stay_bad** samples — confirm they are not mislabeled rescues.
- [ ] **[CHECK]** Spot-check that trajectory first/last numbers in the markdown match a manual read of the CoT (judge errors happen).
- [ ] **[CHECK]** Confirm you understand MRF vs gap_at_start (Aditya README “Reading the plots” + `docs/ACH.md`).
- [ ] **[CHECK]** Glance at `factor.json` for each centered model; note if gap_at_start is large (H4).

## Optional but high value

- [ ] **[CHECK]** Recompute one headline number yourself, e.g. count rescues for Claude `above_good` with a one-liner.
- [ ] Skim Aditya mega-panel (`vendor/value-leakage/mega_panel.png`) start-above / start-below columns for Qwen 122B.

## Do not skip when writing the SPAR doc later

- [ ] Include **random** (not cherry-picked) CoT excerpts in the write-up.  
- [ ] State limitations: summarized Claude CoTs if applicable; trajectory judge errors; regex taxonomy is provisional.  
- [ ] Hours spent (Aditya asked for a note if under 5h on the take-home).

## Verification log

| Date | What I checked | Verdict |
|------|----------------|---------|
| | | |
