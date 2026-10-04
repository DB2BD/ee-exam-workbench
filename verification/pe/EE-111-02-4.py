"""EE-111-02-4 independent check: shunt-series (current-current) feedback, Q1 CE + Q2 CC.

Givens (official crop): VA = inf (ro = inf); Iin drives Q1 base; Q1 collector -> RC to VCC and
Q2 base; Q2 emitter current Io flows down through RL (device) to node x; RF from x back to
Q1 base; an ideal bias current source from x to ground (AC open). No numerical values.
Boxed answers (strict g-parameter two-port, If defined leaving the input node):
  beta_f = -1; RiA = r_pi1; A = -gm1 r_pi1 (1+b) RC / [RC + r_pi2 + (1+b)(RL+RF)];
  Af = A/(1+A beta_f); Rif = r_pi1/(1+|A|); Rof = RoA (1+|A|), RoA = RL + RF + (RC+r_pi2)/(1+b).
Method: exact small-signal nodal solve (SymPy), independent of the two-port decomposition;
the two differ only by the RF feed-forward term, checked symbolically and numerically.
"""
import sympy as sp

rp1, rp2, gm1, b, RC, RL, RF, Iin = sp.symbols("r_pi1 r_pi2 g_m1 beta R_C R_L R_F I_in", positive=True)
vb, vc, ib2, Io, vx, ve, It = sp.symbols("v_b v_c i_b2 I_o v_x v_e I_t")


def nodal(i_in, test_current=None):
    """Exact nodal solution; with test_current the device RL is replaced by that loop current."""
    i_loop = Io if test_current is None else test_current
    eqs = [
        sp.Eq(vb / rp1, i_in + (vx - vb) / RF),          # Q1 base node
        sp.Eq(i_loop, (vx - vb) / RF),                   # node x: bias source AC open
        sp.Eq(-vc / RC - gm1 * vb, ib2),                 # Q1 collector / Q2 base node
        sp.Eq(vc - ve, ib2 * rp2),                       # Q2 base-emitter
        sp.Eq(i_loop, (b + 1) * ib2),                    # Q2 emitter current
    ]
    unknowns = [vb, vc, ib2, vx, ve]
    if test_current is None:
        eqs.append(sp.Eq(ve - vx, Io * RL))
        unknowns.append(Io)
    return sp.solve(eqs, unknowns, dict=True)[0]


s = nodal(Iin)
If = sp.simplify((s[vb] - s[vx]) / RF)               # current leaving the input node through RF
beta_f_exact = sp.simplify(If / s[Io])
Af_exact = sp.simplify(s[Io] / Iin)
Rin_exact = sp.simplify(s[vb] / Iin)
s0 = nodal(0, test_current=It)
Rout_exact = sp.simplify((s0[vx] - s0[ve]) / It)     # seen by the device (RL excluded)

# boxed two-port answers
beta_f = -1
RiA = rp1
den = RC + rp2 + (b + 1) * (RL + RF)
A = -gm1 * rp1 * (b + 1) * RC / den
Af = A / (1 + A * beta_f)
Rif = RiA / (1 + A * beta_f)
RoA = RL + RF + (RC + rp2) / (b + 1)
Rof = RoA * (1 + A * beta_f)

assert beta_f_exact == beta_f                                  # (1) exact
assert sp.simplify(A * beta_f + A) == 0 and (A * beta_f).is_positive   # loop gain = |A| > 0
assert sp.simplify(Rof - (RL + RF + (RC + rp2) / (b + 1) + gm1 * rp1 * RC)) == 0   # expanded form
assert sp.simplify(sp.limit(Af, gm1, sp.oo) - sp.limit(Af_exact, gm1, sp.oo)) == 0
assert sp.simplify(sp.limit(Af_exact, gm1, sp.oo) - sp.Rational(1, beta_f)) == 0
# feed-forward identities (exact vs two-port)
assert sp.simplify(1 / Rin_exact - (1 / Rif + 1 / RoA)) == 0      # Rin_exact = Rif || RoA
assert sp.simplify(Rout_exact - (Rof.subs(RL, 0) + rp1)) == 0      # Rout_exact = Rof(RL->0) + r_pi1


def rel(x, y):
    return abs(float(x) / float(y) - 1)


for vals in ({rp1: 2500, rp2: 250, gm1: 0.04, b: 100, RC: 10000, RL: 100, RF: 1000},
             {rp1: 5000, rp2: 500, gm1: 0.02, b: 100, RC: 30000, RL: 50, RF: 2000}):
    num = {k: e.subs(vals) for k, e in dict(Af=Af, Af_x=Af_exact, Rif=Rif, Rin_x=Rin_exact,
                                              Rof0=Rof.subs(RL, 0), Rout_x=Rout_exact).items()}
    assert rel(num["Af"], num["Af_x"]) < 0.005
    assert rel(num["Rif"], num["Rin_x"]) < 0.005
    assert rel(num["Rof0"], num["Rout_x"]) < 0.005
    print({k: round(float(v), 6) for k, v in num.items()})
print("PASS EE-111-02-4")
