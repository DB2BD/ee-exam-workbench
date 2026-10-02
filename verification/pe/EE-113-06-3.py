"""EE-113-06-3: arc-furnace flicker at main-transformer LV bus, Sb = 3 MVA, and series reactor."""
import sympy as sp

Sb = sp.Rational(3)
Xs = Sb / 1500
XT1 = sp.Rational(6, 100) * Sb / 7
XT2 = sp.Rational(5, 100)
XF = sp.Rational(41, 100)
Xu, Xd = Xs + XT1, XT2 + XF
dV = Xu / (Xu + Xd)
assert abs(float(dV) * 100 - 5.6825) / 5.6825 < 0.005
XR = sp.symbols("XR", positive=True)
xr = sp.solve(sp.Eq(Xu / (Xu + Xd + XR), sp.Rational(45, 10000)), XR)[0]
assert abs(float(xr) - 5.6710) / 5.6710 < 0.005
# independent: KVL with the reactor -> bus voltage step equals 0.45 %
I = 1 / (Xu + Xd + xr)
assert abs(float(I * Xu) - 0.0045) < 1e-12
SR = float(xr * Sb)                    # MVA at base (= furnace transformer rated) current
assert abs(SR - 17.01) / 17.01 < 0.005
ohm = float(xr) * 22.8**2 / 3
assert abs(ohm - 982.7) / 982.7 < 0.005
print("PASS EE-113-06-3")
