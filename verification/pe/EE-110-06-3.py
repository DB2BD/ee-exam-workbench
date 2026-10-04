"""EE-110-06-3: capacitor sizing to keep (一) a 1000 kVA generator and (二) a 1000 kVA transformer within kVA rating.

(一) gen 800 kW / 1000 kVA at PF 0.8 lag + 150 kW at PF 0.75 lag; (二) 1000 kVA at PF 0.8 lag + 100 kVA at PF 1.0.
"""
import numpy as np

def need(loads, s_rated):
    s = sum(kva * complex(pf, np.sqrt(1 - pf**2)) for kva, pf in loads)
    q_allow = np.sqrt(s_rated**2 - s.real**2)
    return s.real, s.imag, s.imag - q_allow

p1, q1, qc1 = need([(1000, 0.8), (150 / 0.75, 0.75)], 1000)
assert abs(p1 - 950) < 1e-9 and abs(qc1 - 420.04) / 420.04 < 0.005     # boxed 420.04 kvar
assert p1 > 800                                                        # prime-mover kW limit exceeded (caveat)
p2, q2, qc2 = need([(1000, 0.8), (100, 1.0)], 1000)
assert abs(qc2 - 164.11) / 164.11 < 0.005                              # boxed 164.11 kvar
# independent: after compensation |S| equals rating and PF = P/S
for p, q, qc in ((p1, q1, qc1), (p2, q2, qc2)):
    assert abs(abs(complex(p, q - qc)) - 1000) < 1e-9
assert abs(p1 / 1000 - 0.95) < 1e-12 and abs(p2 / 1000 - 0.90) < 1e-12
print("PASS EE-110-06-3")
