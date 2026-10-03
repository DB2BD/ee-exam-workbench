"""EE-106-02-5 independent check: non-inverting buck-boost (Q1 and Q2 switch together).

Givens (official crop): Q1 in series with L, D1 from ground to the Q1-L node (cathode up), Q2 from the L-D2 node to ground, D2 to the output;
Q1, Q2 driven synchronously with duty D, frequency f, CCM.  No numbers are given: symbolic result.
Method: inductor volt-second balance, charge balance, triangular inductor current -> Q1 rms.
The numerical instance (Vin = 12 V, D = 0.4, R = 10 ohm, L = 100 uH, f = 25 kHz) is only a numerical check of the symbolic formulas.
"""
import numpy as np
import sympy as sp

D, Vin, Vo, R, L, f = sp.symbols("D Vin Vo R L f", positive=True)
# volt-second balance: Vin*D - Vo*(1-D) = 0
Vo_sol = sp.solve(sp.Eq(Vin * D - Vo * (1 - D), 0), Vo)[0]
assert sp.simplify(Vo_sol - Vin * D / (1 - D)) == 0
IL = Vo_sol / ((1 - D) * R)                          # Io = (1-D) IL
dIL = Vin * D / (L * f)
# Q1 carries iL during DT: rms^2 = D * (IL^2 + dIL^2/12)
t = sp.symbols("t")
iL = IL - dIL / 2 + dIL * t / (D / f)                # rising ramp over 0..D/f
rms2 = sp.integrate(iL**2, (t, 0, D / f)) * f        # (1/T) integral
assert sp.simplify(rms2 - D * (IL**2 + dIL**2 / 12)) == 0
approx = IL * sp.sqrt(D)
# numeric instance
vals = {Vin: 12, D: sp.Rational(2, 5), R: 10, L: sp.Rational(100, 10**6), f: 25_000}
Vo_n = Vo_sol.subs(vals)
IL_n, dIL_n = IL.subs(vals), dIL.subs(vals)
exact_n, approx_n = sp.sqrt(rms2.subs(vals)), approx.subs(vals)
assert abs(float(Vo_n) - 8) < 1e-9 and abs(float(IL_n) - 4 / 3) < 1e-9 and abs(float(dIL_n) - 1.92) < 1e-9
assert float(exact_n) > float(approx_n)
# time-domain simulation of the two states
Vin_n, D_n, R_n, L_n, f_n = 12.0, 0.4, 10.0, 100e-6, 25_000.0
Tn = 1 / f_n
Vo_s = Vin_n * D_n / (1 - D_n)
n = 400_000
tt = np.linspace(0, Tn, n, endpoint=False)
on = tt < D_n * Tn
slope = np.where(on, Vin_n / L_n, -Vo_s / L_n)
il = np.cumsum(slope) * (tt[1] - tt[0])
il = il - il.mean() + float(IL_n)                      # steady-state: average set by charge balance
q1 = np.where(on, il, 0.0)
rms_sim = np.sqrt(np.mean(q1**2))
assert abs(rms_sim - float(exact_n)) / float(exact_n) < 0.005
# power balance
assert abs(float(Vin_n * D_n * IL_n) - Vo_s**2 / R_n) < 1e-9
print(f"Vo/Vin={Vo_sol/Vin}; numeric instance: Vo={float(Vo_n):.3f} IL={float(IL_n):.4f} dIL={float(dIL_n):.3f} IQ1rms exact={float(exact_n):.4f} approx={float(approx_n):.4f}")
print("PASS EE-106-02-5")
