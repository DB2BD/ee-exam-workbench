"""EE-112-06-3: MVA method vs per-unit ohmic check for F1, F2, F3."""
import math

S_src, S_tr = 200.0, 1.0 / 0.10
S_line = 0.38**2 / 0.0722
def ser(*s): return 1 / sum(1 / x for x in s)
S1, S2, S3 = S_src, ser(S_src, S_tr), ser(S_src, S_tr, S_line)
I1 = S1 / (math.sqrt(3) * 11.4); I2 = S2 / (math.sqrt(3) * 0.38); I3 = S3 / (math.sqrt(3) * 0.38)
# ohmic check on 380 V side
Zs = 0.38**2 / 200; Zt = 0.10 * 0.38**2 / 1.0
I3b = 0.38 / (math.sqrt(3) * (Zs + Zt + 0.0722))
assert abs(I3 - I3b) < 1e-9
for got, exp in ((I1, 10.129), (I2, 14.470), (I3, 2.511)):
    assert abs(got - exp) / exp < 0.005
print("PASS EE-112-06-3")
