"""oi_buckets.py — OI bucket thresholds and classification (pure functions).

Extracted from oi_viewer.py (quest Step 3) as the first seam: the smallest
coherent calculation in the viewer. These two functions decide the level
(0-5) of every heatmap cell and every element of the similarity feature
vector, and they depend on nothing else in the app — no Tk, no network,
no calendar state, just the OIranges table and an OI value.

Callers (unchanged): render(), _update_render(), build_feature_vector()
in oi_viewer.py all call these the same way they always did.
"""

import pandas as pd


def effective_thresholds(tier: str, ranges: pd.DataFrame, offsets: list[int]) -> dict:
    """
    {offset: {"call": [p25,p50,p75,p90], "put": [p25,p50,p75,p90]}}
    Non-Regular tiers scale the Regular thresholds by their median adj multiplier.
    """
    reg = ranges[ranges["Tier"] == "0DTE_Regular"].set_index("StrikeOffset")
    adj = (ranges[ranges["Tier"] == tier].set_index("StrikeOffset")
           if tier != "0DTE_Regular" else None)

    out = {}
    for o in offsets:
        if o not in reg.index:
            out[o] = {"call": [0]*4, "put": [0]*4}
            continue
        r  = reg.loc[o]
        cp = [r["Call_p25"], r["Call_p50"], r["Call_p75"], r["Call_p90"]]
        pp = [r["Put_p25"],  r["Put_p50"],  r["Put_p75"],  r["Put_p90"]]
        if adj is not None and o in adj.index:
            ca = float(adj.loc[o, "Call_adj"] or 1.0)
            pa = float(adj.loc[o, "Put_adj"]  or 1.0)
            cp = [v * ca for v in cp]
            pp = [v * pa for v in pp]
        out[o] = {"call": cp, "put": pp}
    return out


def oi_bucket(oi: float, thresholds: list) -> int:
    if oi == 0:
        return 0
    p25, p50, p75, p90 = thresholds
    if oi < p25: return 1
    if oi < p50: return 2
    if oi < p75: return 3
    if oi < p90: return 4
    return 5
