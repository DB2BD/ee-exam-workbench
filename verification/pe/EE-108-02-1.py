"""EE-108-02-1 independent check: single-pole op-amp, A0 = 80 dB, |A(10 kHz)| = 40 dB.

Givens (official crop): |A(f->0)| = 80 dB, |A(10 kHz)| = 40 dB, single pole.
Method: A(f) = A0/(1 + j f/fb); solve fb from the 10 kHz point, ft from |A(ft)| = 1,
then check phase/magnitude at the Bode landmarks (fb/100 ... 10 ft).
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


A0 = sp.Integer(10) ** sp.Rational(80, 20)
A1 = sp.Integer(10) ** sp.Rational(40, 20)
f1 = 10_000
fb, ft = sp.symbols("fb ft", positive=True)
fb_sol = sp.solve(sp.Eq(A0**2 / (1 + (f1 / fb) ** 2), A1**2), fb)[0]
ft_sol = sp.solve(sp.Eq(A0**2 / (1 + (ft / fb_sol) ** 2), 1), ft)[0]


def mag_db(f):
    return float(20 * sp.log(A0 / sp.sqrt(1 + (f / fb_sol) ** 2), 10))


def phase_deg(f):
    return float(-sp.atan(f / fb_sol) * 180 / sp.pi)


assert close(A0, 1e4) and close(A1, 100)
assert close(fb_sol, 100.005) and close(ft_sol, 1.00005e6)
assert abs(mag_db(float(fb_sol)) - 76.9897) < 0.01 and abs(phase_deg(float(fb_sol)) + 45) < 1e-9
assert abs(mag_db(float(ft_sol))) < 1e-9 and abs(mag_db(1e4) - 40) < 1e-9
assert close(phase_deg(float(fb_sol) / 100), -0.5729) and close(phase_deg(10 * float(ft_sol)), -89.99427)
assert close(float(fb_sol) / 100, 1.00005) and close(10 * float(ft_sol), 1.00005e7)
print(f"fb={float(fb_sol):.4f} Hz ft={float(ft_sol):.2f} Hz phase(10kHz)={phase_deg(1e4):.3f} deg")
print("PASS EE-108-02-1")
