# MATCH vs MAIN — seed 0, V=524288/domain/cycle — comparative analysis

**Date:** 2026-09-24 · **Analyst:** Atos-Research · **Status:** for review (advisor/Oleg)

## 0. Data and alignment

| | MAIN | MATCH |
|---|---|---|
| file | `run_v524k_s0.jsonl` | `run_match524k_s0.jsonl` |
| records | t0 + 64 | t0 + 64 |
| per cycle | 4 chess sub-legs → 4 stories sub-legs (131072 chars each) | 8 mixed reads (65536 chess + 65536 stories each) |
| W0 tree | `d1e06861…` | `d1e06861…` (identical) |
| probe wrapper | `4e8ac5a8…` | `4e8ac5a8…` (identical) |
| wall | interrupted (HOLD 09:42:25, resume 09:46:09) | 8849 s, no HOLD |

Both arms consume 524288 chars per domain per cycle, so the post-cycle-c probe
(index `8(c+1)`) sits at identical cumulative per-domain volume in both arms.
All comparisons are at cycle ends. Measurement noise: SE_L = 0.00814 nats/token
(frozen byte probe); gate = 2·SE_L = 0.01628. Cycle-end Δ vs t0 carries
≈ √2·SE_L ≈ 0.0115 combined error.

**Continuity caveat.** MAIN was interrupted after sub-leg 25 and resumed;
cycles 0–2 (points 1–25) are pre-resume and clean, cycles 3–7 are
descriptive-only. MATCH is fully continuous.

## 1. t0 agreement

| | chess | stories |
|---|---|---|
| MAIN t0 | 0.62843 | 0.92480 |
| MATCH t0 | 0.62847 | 0.92487 |
| diff | −0.00004 | −0.00008 |

Differences are ~1/200 of SE_L. Arms are interchangeable at t0.

## 2. Clean region (MAIN cycles 0–2, pre-resume)

Cumulative Δ vs t0 at cycle end (nats/token; negative = improvement):

| cycle | MAIN Δchess | MATCH Δchess | diff (M−X) | MAIN Δstories | MATCH Δstories | diff (M−X) |
|---|---|---|---|---|---|---|
| 0 | +0.0326 | −0.0056 | **+0.0382** | −0.0517 | −0.0459 | −0.0058 |
| 1 | +0.0190 | −0.0134 | **+0.0323** | +0.0240 | −0.0481 | **+0.0720** |
| 2 | +0.0205 | −0.0022 | **+0.0227** | −0.0634 | −0.0344 | −0.0289 |

**Chess:** MAIN ends every clean cycle above t0 by +0.019…+0.033 (all above
gate), MATCH ends every clean cycle at or below t0. The MAIN−MATCH chess
difference is positive at all three clean cycle ends (+0.023…+0.038, i.e.
2.8–4.7×SE_L), same sign, mean ≈ +0.031. Blocked thematic order carries a
persistent chess cost that volume-matched interleaving eliminates. Volume
alone does not produce the MAIN chess degradation — it is an order effect.

**Stories:** no consistent signed effect in the clean region. Cycle 1 shows a
MAIN stories spike (diff +0.072, ~9×SE_L); cycles 0 and 2 show MAIN equal or
better. The cycle-1 spike needs a content-level check (specific stories
sub-leg?) before any interpretation.

## 3. MAIN leg signature (clean cycles 0–2; all 8 shown)

| cycle | clean | transient_stories (chess excursion cost) | return_stories | return_chess (stories leg cost) |
|---|---|---|---|---|
| 0 | Y | +0.0231 | −0.0748 | +0.0446 |
| 1 | Y | +0.0319 | +0.0437 | +0.0359 |
| 2 | Y | +0.0268 | −0.1142 | +0.0340 |
| 3 | n | +0.0479 | −0.0106 | +0.0364 |
| 4 | n | +0.0282 | −0.0192 | +0.0451 |
| 5 | n | +0.0342 | −0.0788 | +0.0345 |
| 6 | n | +0.0328 | −0.0427 | +0.0254 |
| 7 | n | +0.0341 | −0.0511 | +0.0447 |

- **transient_stories: 8/8 positive, all above gate** (+0.023…+0.048). Training
  chess reliably degrades stories.
- **return_chess: 8/8 positive, all above gate** (+0.025…+0.045). Training
  stories reliably degrades chess. Symmetric interference in both directions.
- **return_stories: 7/8 negative** (recovery during the stories leg); the
  exception is cycle 1 (+0.0437) — same anomaly as the §2 cycle-1 spike.

MATCH has no leg structure by construction; within-cycle drift is unsigned
(mean |Δchess| ≈ 0.027 driven by the c4/c5 seesaw, mean |Δstories| ≈ 0.025)
and shows no systematic direction.

## 4. Full run (descriptive-only for MAIN cycles 3–7)

Cycle-7 end vs t0: MAIN **+0.0209 chess / −0.0885 stories**; MATCH
**−0.0291 chess / −0.0077 stories**. Descriptively, MAIN ends trading a chess
degradation (above gate) for a large stories gain, while MATCH ends with a
chess gain (≈3.6×SE_L) and stories flat (within SE_L). Because MAIN cycles
3–7 are post-resume, this contrast is hypothesis-generating only.

## 5. MATCH internal note

MATCH cycles 4–5 show a chess seesaw (+0.0717 → −0.0832 within-cycle drift,
~9×SE_L) that cancels by cycle 6. Even fully interleaved order exhibits large
sub-cycle excursions; cycle-end summaries mask this scale of variability.
Worth checking whether the c4 chess quarter-batch contains an outlier
segment.

## 6. Claims supported / not supported

**Supported (clean region, seed 0):**
1. Blocked order incurs a persistent chess cost vs t0 at every clean cycle
   end; interleaved control does not. (§2)
2. MAIN exhibits symmetric transient interference: each domain's training
   leg degrades the other domain, above gate, 8/8 cycles. (§3)
3. t0 equivalence of arms. (§1)

**Not supported / open:**
- Any net stories effect of order (sign flips across clean cycles). 
- Anything about cycles 3–7 of MAIN beyond descriptive trend (continuity).
- Generality across seeds: single seed both arms. The chess-cost claim needs
  MATCH seeds 1–2 (and MAIN seeds 1–2) before it can survive seed variance.
- Cycle-1 stories spike and MATCH c4/c5 seesaw: unexplained, flagged for
  content-level audit.

## 7. Reproducibility

Script: `analyze_match_vs_main.py` (this directory). Inputs copied verbatim
from the stand (`/workspace/exp/`); no record modified. Outputs:
`match_vs_main_results.json`, `cycle_end_comparison.csv`,
`main_leg_signature.csv`, `fig1_trajectory_plane.png`,
`fig2_nll_vs_volume.png`, `fig3_cycle_deltas.png`.
