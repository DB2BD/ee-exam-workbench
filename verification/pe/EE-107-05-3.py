"""EE-107-05-3: 24 kV, 850 MVA, Xs=100 % generator; 25/345 kV, 850 MVA, X=20 % step-up
transformer; infinite bus 345 kV; 800 MW output at rated terminal voltage.
Base: 850 MVA, 24 kV at generator (345*24/25 = 331.2 kV on the HV side).
"""
import cmath
import math

Sb = 850.0
Vb_gen = 24.0
Vb_hv = 345.0 * 24.0 / 25.0
Xs = 1.0
XT = 0.20 * (25.0 / 24.0) ** 2
Vinf = 345.0 / Vb_hv
P = 800.0 / Sb
Vt = 1.0


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


close(XT, 0.21701, 1e-4)
close(Vinf, 1.04167, 1e-4)
# circuit: E - jXs - Vt - jXT - Vinf  (series)
d = math.asin(P * XT / (Vt * Vinf))
close(math.degrees(d), 11.308, 1e-3)
Vtc = Vt
Vinfc = Vinf * cmath.exp(-1j * d)
I = (Vtc - Vinfc) / (1j * XT)
Sg = Vtc * I.conjugate() * Sb
close(Sg.real, 800.0, 1e-6)
close(Sg.imag, -84.0, 1e-3)
assert Sg.imag < 0   # leading (absorbs vars)
close(abs(Sg), 804.40, 1e-4)
# transformer HV terminal -> infinite bus
Sinf = Vinfc * I.conjugate() * Sb
close(Sinf.real, 800.0, 1e-6)
close(Sinf.imag, -249.2, 1e-3)
close(abs(Sinf), 837.91, 1e-4)
assert abs(Sinf) < 850.0 and abs(Sg) < 850.0
# series loss check: Q difference = I^2 XT
close(Sg.imag - Sinf.imag, abs(I) ** 2 * XT * Sb, 1e-6)
# internal EMF for the circuit model (not asked): E = Vt + jXs I
E = Vtc + 1j * Xs * I
print(f"E={abs(E):.4f}")
print("PASS EE-107-05-3")
