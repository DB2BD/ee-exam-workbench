"""EE-114-06-5: stepped capacitor bank (6 x 50 kvar) for PF >= 0.95 lagging.

Method: complex power sums and exhaustive search over 0..6 steps.
"""
import numpy as np

def S(P, pf): return P + 1j * P * np.tan(np.arccos(pf))
periods = {"off": S(200, 0.85), "peak": S(200, 0.85) + S(100, 0.70)}
tan_t = np.tan(np.arccos(0.95))
need = {k: v.imag - v.real * tan_t for k, v in periods.items()}
assert abs(need["off"] - 58.21) / 58.21 < 0.005
assert abs(need["peak"] - 127.36) / 127.36 < 0.005
res = {}
for k, s in periods.items():
    for n in range(7):
        snew = s - 1j * 50 * n
        pf = snew.real / abs(snew)
        if pf >= 0.95 and snew.imag >= 0:
            res[k] = (n, pf); break
assert res["off"][0] == 2 and abs(res["off"][1] - 0.9929) < 0.0005
assert res["peak"][0] == 3 and abs(res["peak"][1] - 0.9694) < 0.0005
print("PASS EE-114-06-5")
