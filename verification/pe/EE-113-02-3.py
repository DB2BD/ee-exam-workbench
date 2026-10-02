"""EE-113-02-3 independent check: Buck converter in BCM (symbolic).

Givens (official crop): Vs -> series switch S -> node x -> L -> output (C || R);
D1 anode ground, cathode node x. fs, D, ideal, BCM.
Method: piecewise-linear inductor waveform + capacitor charge integration in SymPy;
ripple obtained by integrating i_C = iL - Io over the positive area (not from the
textbook formula), then compared with the closed forms in the note.
"""
import sympy as sp

Vs, D, R, fs, L, C, t = sp.symbols("V_s D R f_s L C t", positive=True)
Vo = sp.symbols("V_o", positive=True)
T = 1 / fs
# volt-second balance
Vo_sol = sp.solve(sp.Eq((Vs - Vo) * D * T + (-Vo) * (1 - D) * T, 0), Vo)[0]
assert sp.simplify(Vo_sol - D * Vs) == 0
Ipk = (Vs - Vo_sol) * D * T / L
fall = Vo_sol * (1 - D) * T / L
assert sp.simplify(Ipk - fall) == 0              # BCM: rise = fall, starts/ends at 0
Io = Vo_sol / R
# average of triangular iL over one period equals Io  ->  L at the boundary
Lb = sp.solve(sp.Eq(Ipk / 2, Io), L)[0]
assert sp.simplify(Lb - (1 - D) * R / (2 * fs)) == 0
Ipk_b = sp.simplify(Ipk.subs(L, Lb))
assert sp.simplify(Ipk_b - 2 * D * Vs / R) == 0
assert sp.simplify(Ipk - Vs * D * (1 - D) / (L * fs)) == 0

# ripple: integrate positive part of iC = iL - Io over one period at L = Lb
iL_on = Ipk_b * t / (D * T)
iL_off = Ipk_b * (1 - (t - D * T) / ((1 - D) * T))
t1 = sp.solve(sp.Eq(iL_on, Io), t)[0]
t2 = sp.solve(sp.Eq(iL_off, Io), t)[0]
dQ = sp.integrate(iL_on - Io, (t, t1, D * T)) + sp.integrate(iL_off - Io, (t, D * T, t2))
ratio = sp.simplify(dQ / C / Vo_sol)
assert sp.simplify(ratio - 1 / (4 * R * C * fs)) == 0
assert sp.simplify(ratio - ((1 - D) / (8 * L * C * fs**2)).subs(L, Lb)) == 0

# numeric spot check used in the note (illustrative values)
vals = {Vs: 12, D: sp.Rational(2, 5), R: 10, fs: 25000, C: sp.Rational(1, 10000)}
assert sp.nsimplify(Lb.subs(vals)) == sp.Rational(120, 10**6)
assert abs(float((ratio * Vo_sol).subs(vals)) - 0.048) < 1e-12
print("Vo=D*Vs, ILmax=2DVs/R, Lmin=(1-D)R/(2fs), dVo/Vo=1/(4RCfs)")
print("PASS EE-113-02-3")
