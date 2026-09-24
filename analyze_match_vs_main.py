#!/usr/bin/env python3
"""MATCH vs MAIN, seed 0, V=524288 per domain per cycle — comparative analysis.

Arms:
  MAIN  (run_v524k_s0.jsonl)      : per cycle 4 chess sub-legs then 4 stories
                                    sub-legs, 131072 chars each (excursion/return).
  MATCH (run_match524k_s0.jsonl)  : same bytes, 8 mixed reads of 131072 chars
                                    (65536 chess + 65536 stories) per cycle.

Alignment: both arms consume 524288 chars per domain per cycle, so
post-cycle-c probe index 8*(c+1) coincides in cumulative per-domain volume.
MAIN continuity caveat: HOLD 09:42:25 / resume 09:46:09 after 25 sub-legs;
points 26..64 (cycles 3..7) are descriptive-only.
"""
import json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SE_L = 0.00814
GATE = 2 * SE_L  # 0.01628

def load(path):
    recs = [json.loads(l) for l in open(path)]
    t0 = next(r for r in recs if r.get("phase") == "t0" or r.get("leg") == "start")
    pts = [r for r in recs if r is not t0]
    pts.sort(key=lambda r: r["ts"])
    return t0, pts

t0_m, main = load("run_v524k_s0.jsonl")
t0_x, match = load("run_match524k_s0.jsonl")
assert len(main) == 64 and len(match) == 64, (len(main), len(match))

def vol_index_after_cycle(c):  # 0-based probe index of last read of cycle c
    return 8 * (c + 1) - 1

out = {"SE_L": SE_L, "gate": GATE,
       "t0": {"MAIN": [t0_m["nll_chess"], t0_m["nll_stories"]],
              "MATCH": [t0_x["nll_chess"], t0_x["nll_stories"]]},
       "t0_diff": [t0_m["nll_chess"] - t0_x["nll_chess"],
                   t0_m["nll_stories"] - t0_x["nll_stories"]],
       "cycles": []}

for c in range(8):
    i = vol_index_after_cycle(c)
    row = {"cycle": c, "clean_MAIN": c <= 2,  # cycles 0-2 fully pre-resume
           "MAIN":   {"chess": main[i]["nll_chess"],  "stories": main[i]["nll_stories"]},
           "MATCH":  {"chess": match[i]["nll_chess"], "stories": match[i]["nll_stories"]}}
    for arm, pts in (("MAIN", main), ("MATCH", match)):
        base = t0_m if arm == "MAIN" else t0_x
        row[arm]["D_chess"]   = pts[i]["nll_chess"]   - base["nll_chess"]
        row[arm]["D_stories"] = pts[i]["nll_stories"] - base["nll_stories"]
    row["diff_D_chess"]   = row["MAIN"]["D_chess"]   - row["MATCH"]["D_chess"]
    row["diff_D_stories"] = row["MAIN"]["D_stories"] - row["MATCH"]["D_stories"]
    out["cycles"].append(row)

# MAIN hysteresis signature per cycle: excursion-end (after chess) vs return-end
out["main_legs"] = []
for c in range(8):
    exc = main[8*c + 3]   # after 4th chess sub-leg
    ret = main[8*c + 7]   # after 4th stories sub-leg
    out["main_legs"].append({
        "cycle": c, "clean_MAIN": c <= 2,
        "exc_chess": exc["nll_chess"], "exc_stories": exc["nll_stories"],
        "ret_chess": ret["nll_chess"], "ret_stories": ret["nll_stories"],
        "transient_stories": exc["nll_stories"] - (main[8*c-1]["nll_stories"] if c else t0_m["nll_stories"]),
        "return_stories":    ret["nll_stories"] - exc["nll_stories"],
        "return_chess":      ret["nll_chess"]   - exc["nll_chess"],
    })

# MATCH within-cycle drift (no leg structure): cycle start -> end
out["match_within"] = []
for c in range(8):
    start = match[8*c - 1] if c else t0_x
    end = match[8*c + 7]
    out["match_within"].append({
        "cycle": c,
        "D_chess": end["nll_chess"] - start["nll_chess"],
        "D_stories": end["nll_stories"] - start["nll_stories"],
    })

json.dump(out, open("match_vs_main_results.json", "w"), indent=1)

# ---- figures ----
def traj(pts, t0):
    xs = [t0["nll_stories"]] + [p["nll_stories"] for p in pts]
    ys = [t0["nll_chess"]]   + [p["nll_chess"]   for p in pts]
    return xs, ys

fig, ax = plt.subplots(figsize=(7, 6))
xs, ys = traj(main, t0_m)
ax.plot(xs, ys, ".-", lw=0.8, ms=4, label="MAIN (blocked legs)")
xs, ys = traj(match, t0_x)
ax.plot(xs, ys, ".-", lw=0.8, ms=4, label="MATCH (mixed reads)")
ax.plot(t0_m["nll_stories"], t0_m["nll_chess"], "k*", ms=14, label="t0")
# mark resume boundary on MAIN
b = main[24]
ax.plot(b["nll_stories"], b["nll_chess"], "rs", ms=9, mfc="none",
        label="MAIN resume boundary (pt 25)")
ax.set_xlabel("NLL stories (nats/token)"); ax.set_ylabel("NLL chess (nats/token)")
ax.legend(); ax.set_title("Trajectories in probe plane, seed 0, V=524288/cycle/domain")
fig.tight_layout(); fig.savefig("fig1_trajectory_plane.png", dpi=150); plt.close(fig)

fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
vol = [(i + 1) * 65536 / 1e6 for i in range(64)]  # Mchars per domain
for axx, key, lab in ((axes[0], "nll_chess", "chess"), (axes[1], "nll_stories", "stories")):
    axx.plot(vol, [p[key] for p in main],  ".-", ms=4, lw=0.8, label="MAIN")
    axx.plot(vol, [p[key] for p in match], ".-", ms=4, lw=0.8, label="MATCH")
    t0v = t0_m[key]
    axx.axhline(t0v, color="k", ls=":", lw=0.8, label=f"t0={t0v:.4f}")
    axx.axvspan(26 * 65536 / 1e6, vol[-1], color="r", alpha=0.06,
                label="MAIN post-resume (descriptive)")
    axx.set_ylabel(f"NLL {lab}"); axx.legend(fontsize=8)
axes[1].set_xlabel("cumulative volume per domain (Mchars)")
axes[0].set_title("Probe NLL vs cumulative per-domain training volume")
fig.tight_layout(); fig.savefig("fig2_nll_vs_volume.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
cy = list(range(8))
dc_m  = [out["cycles"][c]["MAIN"]["D_chess"]   for c in cy]
dc_x  = [out["cycles"][c]["MATCH"]["D_chess"]  for c in cy]
ds_m  = [out["cycles"][c]["MAIN"]["D_stories"] for c in cy]
ds_x  = [out["cycles"][c]["MATCH"]["D_stories"]for c in cy]
w = 0.2
ax.bar([c - 1.5*w for c in cy], dc_m, w, label="MAIN Δchess")
ax.bar([c - 0.5*w for c in cy], dc_x, w, label="MATCH Δchess")
ax.bar([c + 0.5*w for c in cy], ds_m, w, label="MAIN Δstories")
ax.bar([c + 1.5*w for c in cy], ds_x, w, label="MATCH Δstories")
ax.axhline(GATE, color="r", ls="--", lw=0.8); ax.axhline(-GATE, color="r", ls="--", lw=0.8)
ax.text(7.4, GATE, "gate", color="r", fontsize=7, va="bottom")
ax.axvline(2.5, color="k", ls=":", lw=0.8)
ax.text(2.55, ax.get_ylim()[0], "MAIN resume →", fontsize=7)
ax.set_xticks(cy); ax.set_xlabel("cycle (cumulative Δ vs t0 at cycle end)")
ax.set_ylabel("ΔNLL vs t0 (nats/token)"); ax.legend(fontsize=8)
ax.set_title("Cumulative Δ vs t0 at each cycle end")
fig.tight_layout(); fig.savefig("fig3_cycle_deltas.png", dpi=150); plt.close(fig)

# ---- console summary ----
print(f"t0 MAIN  chess {t0_m['nll_chess']:.5f} stories {t0_m['nll_stories']:.5f}")
print(f"t0 MATCH chess {t0_x['nll_chess']:.5f} stories {t0_x['nll_stories']:.5f}")
print(f"t0 diff  chess {out['t0_diff'][0]:+.5f} stories {out['t0_diff'][1]:+.5f} (SE_L {SE_L})")
print("\ncycle | clean | MAIN Dc/Ds | MATCH Dc/Ds | diff Dc/Ds (MAIN-MATCH)")
for r in out["cycles"]:
    print(f"  {r['cycle']}   |  {'Y' if r['clean_MAIN'] else 'n'}   | "
          f"{r['MAIN']['D_chess']:+.5f} {r['MAIN']['D_stories']:+.5f} | "
          f"{r['MATCH']['D_chess']:+.5f} {r['MATCH']['D_stories']:+.5f} | "
          f"{r['diff_D_chess']:+.5f} {r['diff_D_stories']:+.5f}")
print("\nMAIN legs: cyc clean transient_stories return_stories return_chess")
for r in out["main_legs"]:
    print(f"  {r['cycle']}   {'Y' if r['clean_MAIN'] else 'n'}   "
          f"{r['transient_stories']:+.5f}  {r['return_stories']:+.5f}  {r['return_chess']:+.5f}")
print("\nMATCH within-cycle drift:")
for r in out["match_within"]:
    print(f"  {r['cycle']}   {r['D_chess']:+.5f}  {r['D_stories']:+.5f}")
