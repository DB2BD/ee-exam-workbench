"""EE-114-02-4 (descriptive) quantitative arguments for thyristor protection.

Givens (official crop): ideal switch S, DC source VS, thyristor T (+VT-), load (+VL-), series loop.
No numeric values are given; the script checks the symbolic claims used in the note:
 1. KVL VS = VT + VL: blocking T (no load current) -> VT = VS, VL = 0.
 2. Without a snubber the step of VS appears across T in zero time (dv/dt unbounded);
    junction displacement current Cj dv/dt is the false-trigger mechanism.
 3. With an RC snubber (Rs + Cs across T) and a resistive load RL, closing S gives
    vT(0+) = VS*Rs/(RL+Rs) and dvT/dt(0+) = VS*RL/((RL+Rs)^2 Cs), both finite.
 4. A series inductor Ls limits the on-state di/dt to VS/Ls at turn-on.
"""
import sympy as sp

VS, RL, Rs, Cs, Ls, Cj, t = sp.symbols("V_S R_L R_s C_s L_s C_j t", positive=True)

# 1. KVL in the blocking state
VT, VL = sp.symbols("V_T V_L")
blocking = sp.solve([sp.Eq(VS, VT + VL), sp.Eq(VL, 0)], [VT, VL])
assert blocking[VT] == VS and blocking[VL] == 0

# 3. RC snubber across blocking T, resistive load: Laplace solution of the loop
s = sp.symbols("s", positive=True)
Zsn = Rs + 1 / (s * Cs)
I = (VS / s) / (RL + Zsn)
VT_s = sp.simplify(I * Zsn)
vT = sp.simplify(sp.inverse_laplace_transform(VT_s, s, t))
v0 = sp.limit(vT, t, 0, "+")
dv0 = sp.limit(sp.diff(vT, t), t, 0, "+")
assert sp.simplify(v0 - VS * Rs / (RL + Rs)) == 0
assert sp.simplify(dv0 - VS * RL / ((RL + Rs) ** 2 * Cs)) == 0
assert sp.simplify(sp.limit(vT, t, sp.oo) - VS) == 0
# Larger Cs -> smaller dv/dt; with Rs = 0 the slope is VS/(RL Cs)
assert sp.simplify(dv0.subs(Rs, 0) - VS / (RL * Cs)) == 0
assert sp.diff(dv0, Cs).subs({VS: 1, RL: 1, Rs: 1, Cs: 1}) < 0

# 2. Displacement current through junction capacitance is proportional to dv/dt
i_disp = Cj * dv0
assert sp.simplify(i_disp * (RL + Rs) ** 2 * Cs / (Cj * VS * RL)) == 1

# 4. Series inductor: L di/dt = VS - R i  ->  di/dt(0+) = VS/Ls
i = sp.Function("i")
sol = sp.dsolve(sp.Eq(Ls * i(t).diff(t) + RL * i(t), VS), i(t), ics={i(0): 0}).rhs
assert sp.simplify(sp.diff(sol, t).subs(t, 0) - VS / Ls) == 0
print("snubber vT(0+) =", v0, "; dvT/dt(0+) =", sp.simplify(dv0))
print("PASS EE-114-02-4 (descriptive)")
