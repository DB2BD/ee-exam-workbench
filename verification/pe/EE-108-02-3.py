"""EE-108-02-3 independent check: common-source stage with R_S -> series-series (current-series) feedback.

Givens (official crop): MOSFET in saturation, small-signal gm and ro only, load R_L in the drain,
R_S in the source, v_sig at the gate; feedback network = R_S (inside dashed box).
Method:
  1. exact small-signal nodal solution (gate = v_sig, drain node v_o with R_L to ground, source node v_s);
  2. R_of: v_sig = 0, R_L removed, test source at the drain;
  3. ideal-feedback decomposition  A = io/vi (R_S, R_L loading included), beta = R_S,
     A_f = A/(1+A*beta), A_vf = -A_f*R_L, R_of = R_o(1+A0*beta); all must equal the exact results.
"""
import sympy as sp

gm, ro, RL, RS, vsig, vt = sp.symbols("gm ro RL RS vsig vt", positive=True)
vo, vs = sp.symbols("vo vs")


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


# 1. exact gain.  id flows drain -> source:  id = gm (vsig - vs) + (vo - vs)/ro
idr = gm * (vsig - vs) + (vo - vs) / ro
sol = sp.solve([sp.Eq(vo / RL + idr, 0), sp.Eq(idr, vs / RS)], [vo, vs], dict=True)[0]
Avf_exact = sp.simplify(sol[vo] / vsig)
Avf_formula = -gm * ro * RL / (ro + RL + RS + gm * ro * RS)
assert sp.simplify(Avf_exact - Avf_formula) == 0

# 2. exact output resistance looking into the drain (R_L removed)
id_t = -gm * vs + (vt - vs) / ro
vs_t = sp.solve(sp.Eq(id_t, vs / RS), vs)[0]
Rof_exact = sp.simplify(vt / (vs_t / RS))
assert sp.simplify(Rof_exact - (ro + RS + gm * ro * RS)) == 0

# 3. feedback decomposition
A = gm * ro / (ro + RL + RS)          # io/vi, vgs = vi, R_S loads only the output loop
beta = RS                              # v_f / io
Af = A / (1 + A * beta)
assert sp.simplify(Af - gm * ro / (ro + RL + RS + gm * ro * RS)) == 0
assert sp.simplify(-RL * Af - Avf_exact) == 0
A0 = gm * ro / (ro + RS)               # R_L -> 0 (output shorted), for the output resistance
Ro = ro + RS
assert sp.simplify(Ro * (1 + A0 * beta) - Rof_exact) == 0
# limits
assert sp.simplify(sp.limit(Avf_formula, ro, sp.oo) + gm * RL / (1 + gm * RS)) == 0
assert sp.simplify(sp.limit(A, ro, sp.oo) - gm) == 0

# numeric spot check: gm = 2 mS, ro = 50 k, RL = 5 k, RS = 1 k
vals = {gm: 2e-3, ro: 50e3, RL: 5e3, RS: 1e3}
assert close(Avf_formula.subs(vals), -(2e-3 * 50e3 * 5e3) / (50e3 + 5e3 + 1e3 + 2e-3 * 50e3 * 1e3))
assert close(Rof_exact.subs(vals), 50e3 + 1e3 + 100e3)
print("Avf =", Avf_formula, "; Rof =", ro + RS + gm * ro * RS)
print("PASS EE-108-02-3")
