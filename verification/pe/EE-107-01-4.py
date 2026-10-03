"""EE-107-01-4 independent check: maximise power into R_L, solving the whole circuit with an ideal 4:1 transformer.

Givens (official crop): 840/0 V rms source (+ top) -> 60 ohm -> primary dot (top) ... primary
bottom joins the common node N, which also connects to the 20 ohm resistor to ground (b) and to
the secondary BOTTOM terminal (the secondary dot is at the bottom).  Secondary top = a.  R_L between a and b.
Ideal transformer, dot convention: Vp(dot-undotted) = 4*Vs(dot-undotted), Np*Ip_in_dot + Ns*Is_in_dot = 0.
"""
import sympy as sp

RL = sp.symbols("RL", positive=True)
Ip, Ic, VN, Va, Vtop = sp.symbols("Ip Ic VN Va Vtop")
# Ip: current into primary dot (top) ; Ic: current through secondary coil from a (top, undotted) to N (bottom, dot)
# current entering the secondary dot terminal = Ic leaves... entering dot terminal (bottom) is -Ic going up? the
# current Ic flows a -> N inside the coil, so it LEAVES the dot terminal: current entering the dot = -Ic.
eqs = [
    sp.Eq(Vtop, 840 - 60 * Ip),                         # source and 60 ohm
    sp.Eq(VN, 20 * (Ip + Ic)),                          # 20 ohm carries primary return current plus secondary current
    sp.Eq(Vtop - VN, 4 * (VN - Va)),                    # Vp (dot - undotted) = 4 * Vs (dot N - undotted a)
    sp.Eq(4 * Ip + 1 * (-Ic), 0),                       # N1*I_in_dot1 + N2*I_in_dot2 = 0
    sp.Eq(Ic, -Va / RL),                                # KCL at a: Ic leaves a through the coil, load current Va/RL leaves too
]
sol = sp.solve(eqs, [Ip, Ic, VN, Va, Vtop], dict=True)[0]
PL = sp.simplify(sol[Va] ** 2 / RL)
RL_opt = sp.solve(sp.diff(PL, RL), RL)
assert RL_opt == [35], RL_opt
assert sp.simplify(PL.subs(RL, 35)) == 315
# open-circuit voltage (R_L -> infinity)
Voc = sp.limit(sol[Va], RL, sp.oo)
assert Voc == -210
# power balance at the optimum: source power = 60 ohm + 20 ohm + load
s = {k: v.subs(RL, 35) for k, v in sol.items()}
P_src = 840 * s[Ip]
P_loss = 60 * s[Ip] ** 2 + 20 * (s[Ip] + s[Ic]) ** 2 + s[Va] ** 2 / 35
assert sp.simplify(P_src - P_loss) == 0
print("PASS EE-107-01-4")
