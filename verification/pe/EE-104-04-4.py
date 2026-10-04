"""EE-104-04-4: Y-connected 4-pole induction motor, base 2.2 kVA / 380 V; per-unit circuit (Vs=1.0):
rs=0.05, xs=0.15, Rc=30, Xm=40 (shunt after stator branch), rr=0.05, xr=0.15, load (1-s)rr/s. Start: s=1."""
import numpy as np

S, V = 2200.0, 380.0
rs, xs, rr, xr, Rc, Xm = 0.05, 0.15, 0.05, 0.15, 30.0, 40.0
s = 1.0
Ib = S / (np.sqrt(3) * V)
Zl = (1 - s) * rr / s                      # = 0 at start
Zr = rr + 1j * xr + Zl                      # rotor branch keeps r_r in series with the (1-s)r_r/s resistor
Zm = 1 / (1 / Rc + 1 / (1j * Xm))
Zp = Zr * Zm / (Zr + Zm)
Zin = rs + 1j * xs + Zp
Is_pu = 1.0 / abs(Zin)
Is = Is_pu * Ib
assert abs(Ib - 3.3426) / 3.3426 < 0.005
assert abs(Is_pu - 1.0 / abs(Zin)) < 1e-12
assert abs(Is - 10.60) / 10.60 < 0.005 and abs(Is_pu - 3.171) / 3.171 < 0.005
# independent route: 2x2 mesh solve (does not use Zin)
Zs = rs + 1j * xs
M = np.array([[Zs + Zm, -Zm], [-Zm, Zm + Zr]])
I1m, I2m = np.linalg.solve(M, [1.0, 0.0])
assert abs(abs(I1m) - 3.171) / 3.171 < 0.005 and abs(abs(I2m) - 3.154) / 3.154 < 0.005
assert abs(np.degrees(np.angle(I1m)) + 71.46) < 0.1
Vp = Zm * (I1m - I2m)
P_in = (1.0 * np.conj(I1m)).real
P_loss = abs(I1m) ** 2 * rs + abs(I2m) ** 2 * rr + abs(Vp) ** 2 / Rc
assert abs(P_in - 1.0083) < 1e-3 and abs(P_in - P_loss) < 1e-6
print("PASS EE-104-04-4")
