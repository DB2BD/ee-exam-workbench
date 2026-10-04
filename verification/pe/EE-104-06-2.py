"""EE-104-06-2: substation kVA with group diversity factors (table 3 and 2), inter-group 1.1, 10 % loss."""
import numpy as np

# table (crop): connected kW, demand factor, diversity factor, lagging pf
lamp = dict(kw=150, df=1.0, div=3, pf=0.95)
motor = dict(kw=200, df=1.0, div=2, pf=0.80)
div_between = 1.1
loss = 0.10

def group_pq(g):
    p = g["kw"] * g["df"] / g["div"]          # group maximum demand (kW)
    q = p * np.tan(np.arccos(g["pf"]))
    return p, q

pl, ql = group_pq(lamp)
pm, qm = group_pq(motor)
assert abs(pl - 50) < 1e-9 and abs(pm - 100) < 1e-9
S_sum = abs(complex(pl + pm, ql + qm))              # complex sum of group maxima
S_coin = S_sum / div_between
assert abs(S_sum - 175.671) / 175.671 < 0.005
assert abs(S_coin - 159.70) / 159.70 < 0.005
# main answer: loss = 10 % of the power delivered by the substation
S_sub = S_coin / (1 - loss)
assert abs(S_sub - 177.45) / 177.45 < 0.005
# branch: loss = 10 % of the load-end demand
S_sub_b = S_coin * (1 + loss)
assert abs(S_sub_b - 175.67) / 175.67 < 0.005
# independent check: build kW/kvar of the substation output and take |S|
P_out = (pl + pm) / div_between / (1 - loss)
Q_out = (ql + qm) / div_between / (1 - loss)
assert abs(np.hypot(P_out, Q_out) - S_sub) < 1e-9
assert abs(S_sum * 1.1 / 0.9 - 214.7) < 0.1                    # 1.1 wrongly multiplied
assert abs((pl / 0.95 + pm / 0.80) / 1.1 / 0.9 - 179.4) < 0.1   # arithmetic kVA sum
print("PASS EE-104-06-2")
