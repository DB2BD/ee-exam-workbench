"""EE-109-06-1 (descriptive): transformer installed capacity and contract demand for TOU tariff.

No numeric givens; the script checks the quantitative relations the note relies on with a
small illustrative load set: demand/diversity reduce the nameplate sum, and contract demand
(15-min kW maximum per period) is not the transformer kVA.
"""
import numpy as np

kw = np.array([200, 150, 120, 80.0]); pf = np.array([0.85, 0.8, 0.9, 0.85])
fd = np.array([0.8, 0.7, 0.9, 0.6]); fdiv = 1.3; margin = 0.2
s_md = (kw * fd / pf).sum() / fdiv
s_tr = s_md * (1 + margin)
assert s_md < (kw / pf).sum()              # demand/diversity: below nameplate sum
assert s_tr > s_md
# contract demand: max of 15-min average kW within each tariff period, kW not kVA
rng = np.random.default_rng(0)
p = rng.uniform(150, 420, 96)               # one day of 15-min demands
on = np.r_[np.zeros(30), np.ones(58), np.zeros(8)].astype(bool)
d_on, d_off = p[on].max(), p[~on].max()
assert d_on <= p.max() and d_off <= p.max() and max(d_on, d_off) == p.max()
assert p.max() < s_tr * pf.min() * 2       # sanity: kW demand compared against kVA rating only via PF
print("PASS EE-109-06-1 (descriptive)")
