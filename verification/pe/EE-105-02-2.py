"""EE-105-02-2 independent check: inverting amplifier with finite open-loop gain Ao.

Givens: RF=800k, R1=10k, Ao=2e5; Rs=0, vS=100 mV for (3).  Op-amp: vo = Ao*(vp - vn), vp=0
(no current in Rx).  Method: KCL at the inverting node solved with sympy.
"""
import sympy as sp

RF, R1, Ao = sp.Integer(800_000), sp.Integer(10_000), sp.Integer(200_000)
vs, vn, vo = sp.symbols("vs vn vo")
sol = sp.solve([sp.Eq((vs - vn) / R1, (vn - vo) / RF), sp.Eq(vo, -Ao * vn)], [vn, vo], dict=True)[0]
Af = sp.simplify(sol[vo] / vs)
Af_val = float(Af)
vO = Af_val * 0.1
err_gain = (Af_val - (-80)) / (-80)
dv = vO - (-8.0)


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


assert sp.simplify(Af - (-(RF / R1) / (1 + (1 + RF / R1) / Ao))) == 0
assert close(Af_val, -79.9676) and close(vO, -7.9967613)
assert close(err_gain, -4.05e-4, 0.005) and close(dv, 3.2387e-3, 0.001)
assert abs(float(sol[vn].subs(vs, 0.1))) < 5e-5  # vn = -vo/Ao ~ 40 uV
print(f"Af={Af_val:.6f} vO={vO:.7f} V err={err_gain*100:.4f}% dv={dv*1e3:.4f} mV")
print("PASS EE-105-02-2")
