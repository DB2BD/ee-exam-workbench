"""EE-107-06-1: four consumers, diversity factor 1.5 -> coincident maximum, average, load factor, daily kWh.

Table (crop): connected kVA / pf (lag) / demand factor / load factor
A 100/0.85/50 %/45 %, B 60/0.80/55 %/40 %, C 150/0.88/60 %/50 %, D 120/0.90/40 %/35 %.
Individual maximum demand = kVA x demand factor x pf; individual average = maximum x load factor.
"""
rows = {"A": (100, 0.85, 0.50, 0.45), "B": (60, 0.80, 0.55, 0.40),
        "C": (150, 0.88, 0.60, 0.50), "D": (120, 0.90, 0.40, 0.35)}
DIVERSITY = 1.5
pmax = {k: s * df * pf for k, (s, pf, df, lf) in rows.items()}
pavg = {k: pmax[k] * rows[k][3] for k in rows}
assert [round(pmax[k], 2) for k in "ABCD"] == [42.50, 26.40, 79.20, 43.20]
assert [round(pavg[k], 3) for k in "ABCD"] == [19.125, 10.560, 39.600, 15.120]

sum_max = sum(pmax.values())
assert abs(sum_max - 191.30) < 1e-9
p_coinc = sum_max / DIVERSITY
assert abs(p_coinc - 127.533) / 127.533 < 5e-4                # boxed (一)
p_avg = sum(pavg.values())
assert abs(p_avg - 84.405) / 84.405 < 5e-4                    # boxed (二)
lf = p_avg / p_coinc
assert abs(lf - 0.6618) / 0.6618 < 5e-4                       # boxed (三)
e_day = p_avg * 24
assert abs(e_day - 2025.72) / 2025.72 < 5e-4                  # boxed (四)
# group load factor = average / (sum of maxima / diversity) equals DF x (sum avg / sum max)
assert abs(lf - DIVERSITY * p_avg / sum_max) < 1e-12
print("PASS EE-107-06-1")
