# P0 status — complete on 3080

## Results (honest)

**P0a parking:** Confirmed. Below_good “wins” are mostly `estimate == threshold`.

**P0c disclose:** Fail-ish. Only **12.5%** regex-admit; 75–80% “neither”. Asking the 3B to disclose does not work well.

**P0b steer (layer 18):** The interesting result.

| Arm | above %good | below %good | % parked (above/below) | mrf_proxy |
|-----|-------------|-------------|-------------------------|-----------|
| steer **−0.4** | **0.50** | 0.875 | **0.14 / 0.19** | 0.71 |
| steer 0 | 0.25 | 0.625 | 0.56 / 0.56 | −0.29 |
| steer +0.4 | 0.33 | 0.50 | 0.44 / 0.25 | −1.57 (noisy) |
| **random −0.4** | 0.00 | 1.00 | **1.00 / 0.87** | 0.10 |

Condition direction ≠ random: **−α cuts thr-parking**; random **induces** it.

## App narrative
1. Headline: Claude human labels (73% vs 0% intentional_steer).  
2. Local: 3B mostly parks; prompt turn-off/disclose weak; **activation direction mediates parking vs random control** (Gilg-lite, limited claim).  
3. Limitations: n=16 steer, regex parse, 3B ≠ 122B/Claude.

## Next
**Write Neel doc + form.** Optional P1 only after a draft exists.
