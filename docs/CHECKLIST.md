# CHECKLIST — Ben must verify

Anything marked **[CHECK]** is load-bearing. Do not trust agent regex / summaries alone.

## Must do before claiming results

- [x] **[CHECK]** Label required RESCUE CoTs (Claude / Qwen / Inkling).  
      Done 2026-08-24 → 102/102 in `ben_labels.csv`.
- [x] **[CHECK]** Label Claude **CONTROL** samples (stay_bad / stay_good).  
      Done → 20/20. Contrast: rescue `intentional_steer` 73% vs control **0%**. One `mislabeled_is_rescue` (`…CONTROL_stay_good__i16`).
- [x] **[CHECK]** Spot-check trajectory first/last vs CoT (`traj_ok`).  
      121 yes / 1 unsure on labeled rows.
- [ ] **[CHECK]** Confirm you understand MRF vs gap_at_start (Aditya README + `docs/ACH.md`).
- [ ] **[CHECK]** Glance at `factor.json` for each centered model; note if gap_at_start is large (H4).

## Optional but high value

- [ ] Label Qwen / Inkling recommended controls (40 rows) — nice for cross-model control contrast; Claude already carries the main check.
- [ ] **[CHECK]** Recompute one headline number yourself (e.g. Claude above_good rescue count).
- [ ] Skim Aditya mega-panel start-above / start-below for Qwen 122B.
- [ ] Second-rater on a 15–20 row subsample.

## Do not skip when writing the SPAR doc later

- [ ] Include **random** (not cherry-picked) CoT excerpts.  
- [ ] Lead with ACH + Claude rescue↔control contrast table.  
- [ ] State limitations: single rater; Claude summaries; Qwen/Inkling controls unlabeled; no Phase 2 causality yet.  
- [ ] Hours spent note if under 5h take-home.

## Verification log

| Date | What I checked | Verdict |
|------|----------------|---------|
| 2026-08-24 | 102 required RESCUEs | Steer-involved ~91%; Claude 73% intentional_steer |
| 2026-08-25 | 20 Claude recommended controls | 0% intentional_steer; 55% honest_revision; 1 mislabeled_is_rescue |
| | gap_at_start / H4 | Not done |
