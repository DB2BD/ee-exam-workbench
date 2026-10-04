"""EE-105-01-2: Rth with a dependent source (2000*Ix, Ix = current down through 1k). kOhm / V / mA units.
No independent source, so apply a test voltage at A-B and find the current."""
import sympy as sp
V1, VA, Vt = sp.symbols("V1 VA Vt")
Ix = V1 / 1                      # mA, current down the 1k resistor
Vs = 2000 * (Ix * 1e-3)          # volts: 2000 ohm * Ix(A)
Vs = sp.nsimplify(Vs)
VAv = Vt
V1v = sp.solve(sp.Eq((Vs - V1) / 2, V1 / 1 + (V1 - VAv) / 3), V1)[0]
Itest = VAv / 2 + (VAv - V1v) / 3          # mA into A
Rth = sp.simplify(Vt / Itest) * 1000       # ohm
assert sp.simplify(Rth - sp.Rational(10000, 7)) == 0, Rth
print("PASS EE-105-01-2")
