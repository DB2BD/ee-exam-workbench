"""EE-106-06-1: descriptive essay (purpose of short-circuit calculation; purpose/importance of
equipment grounding).  No numeric answer in the stem; the script only checks two quantitative
arguments used in the note's explanation.
"""
import math

# (一) breaker interrupting rating must exceed the prospective fault current:
# 3-phase fault level S_sc = sqrt(3) V I_sc  <->  I_sc = S_sc / (sqrt(3) V)
s_sc, v = 250e6, 11.4e3
i_sc = s_sc / (math.sqrt(3) * v)
assert abs(i_sc - 12.66e3) / 12.66e3 < 1e-3
# thermal withstand scales with I^2 t: halving clearing time at constant current halves I^2 t
assert (i_sc**2 * 0.5) / (i_sc**2 * 1.0) == 0.5
# (二) touch voltage = I_g * R_g: lowering earth resistance lowers the frame potential
i_g = 100.0
assert i_g * 5.0 < i_g * 25.0
print("PASS EE-106-06-1 (descriptive)")
