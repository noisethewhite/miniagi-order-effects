# mini-AGI training-order effects: MATCH vs MAIN, seed 0

Comparative analysis of two volume-matched continual-training arms on a
mini-AGI stand, seed 0, dose V = 524288 chars per domain per cycle, 8 cycles.

- **MAIN** (`data/run_v524k_s0.jsonl`): blocked thematic order — per cycle,
  4 chess sub-legs then 4 stories sub-legs (131072 chars each),
  excursion/return structure.
- **MATCH** (`data/run_match524k_s0.jsonl`): matched-order control — same
  W0, same source bytes, same per-cycle volume and probe cadence, but the
  sub-legs are quartered (32768 chars) and reassembled into 8 balanced mixed
  reads per cycle (65536 chess + 65536 stories each), destroying long
  thematic blocks.

Both arms share W0 (tree `d1e06861…`) and the probe wrapper (`4e8ac5a8…`).
Probe noise SE_L = 0.00814 nats/token; decision gate = 2·SE_L.

**Continuity caveat.** MAIN was interrupted after sub-leg 25 and resumed;
cycles 0–2 (points 1–25) are pre-resume and clean, cycles 3–7 are
descriptive-only. MATCH is fully continuous.

## Headline (clean region, seed 0)

MAIN ends every clean cycle with chess NLL **above** t0 (+0.019…+0.033, all
above gate); MATCH ends every clean cycle at or below t0. The MAIN−MATCH
chess difference is +0.023…+0.038 (2.8–4.7×SE_L), same sign in all three
clean cycles: blocked order carries a persistent chess cost that
volume-matched interleaving eliminates — an order effect, not a volume
effect. MAIN also shows symmetric transient interference (each domain's
training leg degrades the other domain, 8/8 cycles, above gate).

Single seed in both arms; claims await seeds 1–2. See
`match_vs_main_report.md` for the full analysis, tables, limitations.

## Layout

- `match_vs_main_report.md` — full analysis report
- `analyze_match_vs_main.py` — analysis script (reproduces everything below)
- `data/` — raw run logs copied verbatim from the stand (`/workspace/exp/`)
- `results/` — computed tables (JSON + CSV)
- `figures/` — trajectory plane, NLL vs volume, cycle-end deltas

## Reproduce

```
python3 -m venv .venv && .venv/bin/pip install matplotlib numpy
# place data files next to the script (or symlink data/ contents)
.venv/bin/python analyze_match_vs_main.py
```

The script expects `run_v524k_s0.jsonl` and `run_match524k_s0.jsonl` in its
working directory; both are in `data/`.
