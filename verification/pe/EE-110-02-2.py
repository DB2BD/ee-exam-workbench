"""EE-110-02-2 independent check: differential amplifier, CMRR and outputs.

Givens (official crop): CMRR = 20000, Av(d) = 1500, 1 Vrms 60 Hz interference,
500 uVrms signals. Method: vo = Ad*vd + Ac*vcm with vd = v1 - v2, vcm = (v1 + v2)/2,
evaluated per case; CMRR(dB) by log10.
"""
import math


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


CMRR, Ad = 20000, 1500
Ac = Ad / CMRR
cmrr_db = 20 * math.log10(CMRR)


def vo(v1, v2):
    return Ad * (v1 - v2) + Ac * (v1 + v2) / 2


v3 = vo(500e-6, 0)            # (3) single-ended input
v4 = vo(500e-6, -500e-6)      # (4) equal, opposite-phase input
v5 = vo(1.0, 1.0)             # (5) interference common to both inputs
assert close(Ac, 0.075) and close(cmrr_db, 86.02)
assert close(v3, 0.75) and close(v4, 1.5) and close(v5, 0.075)
assert abs(v3 - 0.75) < 2e-5   # common-mode share of (3) is only 18.75 uV
print(f"Ac={Ac} CMRR={cmrr_db:.4f} dB vo3={v3:.8f} vo4={v4} vo5={v5}")
print("PASS EE-110-02-2")
