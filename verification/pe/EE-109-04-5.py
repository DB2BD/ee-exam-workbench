"""EE-109-04-5: variable-reluctance actuator, N = 120, two gaps g = 3 mm, depth h = 1.8 cm,
rotor radius r1 = 2.5 cm, overlap angle theta, iron mu -> inf."""
import sympy as sp

theta, i = sp.symbols("theta i", positive=True)
mu0 = 4 * sp.pi * sp.Rational(1, 10**7)
N, g, h, r1 = 120, sp.Rational(3, 1000), sp.Rational(18, 1000), sp.Rational(25, 1000)
A = h * r1 * theta
R = 2 * g / (mu0 * A)
L = N**2 / R
coef = sp.simplify(L / theta)
assert abs(float(coef) - 1.3572e-3) / 1.3572e-3 <= 0.005
Wc = sp.Rational(1, 2) * L * i**2            # co-energy (linear)
T = sp.diff(Wc, theta).subs({i: 20, theta: sp.pi / 6})
assert abs(float(T) - 0.2714) / 0.2714 <= 0.005
# independent: energy route at constant flux, T = -dW/dtheta with W = lambda^2 / (2L)
lam = sp.symbols("lambda", positive=True)
W = lam**2 / (2 * L)
T_flux = -sp.diff(W, theta).subs(lam, L * i).subs({i: 20, theta: sp.pi / 6})
assert sp.simplify(T_flux - T) == 0
# mean-gap-radius variant (r1 + g/2) for the condition note
coef2 = float(coef) * float((r1 + g / 2) / r1)
print(f"dL/dtheta={float(coef):.6e} H/rad T={float(T):.5f} N.m (mean-radius variant {coef2:.4e}, {200*coef2:.4f})")
print("PASS EE-109-04-5")
