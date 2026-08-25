# CHECKLIST — Ben must verify

Anything marked **[CHECK]** is load-bearing. Do not trust agent regex / summaries alone.

## Must do before claiming results

- [x] **[CHECK]** Label required RESCUE CoTs (Claude / Qwen / Inkling) via labeling packet.  
      Done 2026-08-24 → `labeling_packet/results/ben_labels.csv` (102/102). Folded into `docs/ACH.md`.
- [ ] **[CHECK]** Read ≥5 **CONTROL stay_bad** samples — confirm they are not mislabeled rescues.  
      *(60 recommended control rows still blank in CSV — do a short pass, Claude first.)*
- [x] **[CHECK]** Spot-check trajectory first/last vs CoT (`traj_ok`).  
      101 yes / 1 unsure (`claude-opus-4-7__below_good__RESCUE__i61`).
- [ ] **[CHECK]** Confirm you understand MRF vs gap_at_start (Aditya README “Reading the plots” + `docs/ACH.md`).
- [ ] **[CHECK]** Glance at `factor.json` for each centered model; note if gap_at_start is large (H4).

## Optional but high value

- [ ] Label remaining `priority=recommended` controls (or at least Claude’s 20).
- [ ] **[CHECK]** Recompute one headline number yourself, e.g. count rescues for Claude `above_good` with a one-liner.
- [ ] Skim Aditya mega-panel (`vendor/value-leakage/mega_panel.png`) start-above / start-below columns for Qwen 122B.
- [ ] Second-rater on a 15–20 row subsample (inter-rater on steer vs mixed vs honest).

## Do not skip when writing the SPAR doc later

- [ ] Include **random** (not cherry-picked) CoT excerpts in the write-up.  
- [ ] State limitations: single rater; summarized Claude CoTs if applicable; no control labels yet; trajectory judge errors; regex taxonomy discarded.  
- [ ] Hours spent (Aditya asked for a note if under 5h on the take-home).  
- [ ] Point to ACH table + human label %.

## Verification log

| Date | What I checked | Verdict |
|------|----------------|---------|
| 2026-08-24 | All 102 required RESCUE rows labeled (`intentional_steer` / `mixed` / `honest_revision`) | Steer-involved ~91%; Claude 73% intentional_steer; Qwen often mixed; pure honest ~9%. See `docs/ACH.md`. |
| | Controls (recommended) | Not done |
| | gap_at_start / H4 | Not done |
