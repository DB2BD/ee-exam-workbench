"""EE-109-04-1: 50 kVA 2400/240 V 60 Hz, Np = 1000, Ns = 100, mu -> inf, R = 0,
core loss 500 W, leakage reluctances Rp = 4e8, Rs = 5e6 A.t/Wb."""
import sympy as sp

mu = sp.symbols("mu", positive=True)
w = 2 * sp.pi * 60
Vp, Pcore, Np, Ns_ = 2400, 500, 1000, 100
# magnetizing reactance Xm = w Np^2 / R_M, R_M = l/(mu A) -> 0 as mu -> inf
l, A = sp.symbols("l A", positive=True)
Xm = w * Np**2 * mu * A / l
Im = Vp / Xm
assert sp.limit(Im, mu, sp.oo) == 0
Rc = sp.Rational(Vp**2, Pcore)
Ic = Vp / Rc
Iphi = sp.sqrt(Ic**2 + sp.limit(Im, mu, sp.oo) ** 2)
assert abs(float(Iphi) - 0.2083) / 0.2083 <= 0.005
assert Rc == 11520
# (2) leakage reactance
Xp = w * Np**2 / sp.Integer(4 * 10**8)
assert abs(float(Xp) - 0.9425) / 0.9425 <= 0.005
# independent: excitation power from Iphi equals core loss
assert abs(float(Vp * Iphi) - Pcore) < 1e-9
# secondary leakage referred to primary (not asked): a^2 * w Ns^2 / Rs = w Np^2 / Rs
Xs_ref = (Np / Ns_) ** 2 * w * Ns_**2 / sp.Integer(5 * 10**6)
assert sp.simplify(Xs_ref - w * Np**2 / sp.Integer(5 * 10**6)) == 0
print(f"Iphi={float(Iphi):.5f} A Rc={Rc} ohm Xp={float(Xp):.5f} ohm Xs'={float(Xs_ref):.3f} ohm")
print("PASS EE-109-04-1")
