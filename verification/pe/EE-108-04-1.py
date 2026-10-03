"""EE-108-04-1: 480/120 V, 5 kVA two-winding transformer reconnected as a single-phase
autotransformer, source 600 V, load 480 V.  Only nameplate data are used."""
import numpy as np

S2w, Vc, Vs = 5000.0, 480.0, 120.0       # two-winding rating, common (480 V) and series (120 V) windings
Vh, Vl = 600.0, 480.0                     # source and load voltages given in the stem
# only way to build 600 V from {480, 120} with the load on 480 V: series winding aids the common winding
assert Vc + Vs == Vh and Vc == Vl
Ic_rated, Is_rated = S2w / Vc, S2w / Vs   # 10.4167 A, 41.6667 A
a = Vh / Vl
# ideal autotransformer: I_in through series winding, I_out = a*I_in, common winding carries I_out - I_in
I_in_max_series = Is_rated
I_in_max_common = Ic_rated / (a - 1)
I_in = min(I_in_max_series, I_in_max_common)
assert abs(I_in_max_series - I_in_max_common) < 1e-9     # both windings reach rating together
I_out = a * I_in
S_auto = Vh * I_in
assert abs(S_auto - 25000) / 25000 < 1e-9
assert abs(Vl * I_out - S_auto) < 1e-6
assert abs((I_out - I_in) - Ic_rated) < 1e-9
S_ind = Vs * I_in
S_cond = Vl * I_in
assert abs(S_ind - 5000) < 1e-6 and abs(S_cond - 20000) < 1e-6
assert abs(S_auto / S2w - 5) < 1e-12
print(f"I_in={I_in:.4f} I_out={I_out:.4f} S={S_auto/1e3:.3f} kVA ind={S_ind/1e3:.1f} cond={S_cond/1e3:.1f}")
print("PASS EE-108-04-1")
