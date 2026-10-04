"""EE-104-02-1 independent check: PMOS common-source stage with unbypassed RS (official crop).

Givens: Kp=0.1 mA/V^2, VTP=-0.8 V, lambda=0, IDQ=0.4 mA, VSDQ=4 V, +5 V / -5 V supplies,
gate at 0 V DC (200k to ground carries no current), CL=10 pF, RS unbypassed.
The crop uses the notation Kp / VTP / IDQ / VSDQ with no square-law definition; the primary
convention is ID = Kp (VSG + VTP)^2 (conduction parameter, clean bias values 5.5k / 9.5k).
The alternative ID = (Kp/2)(VSG - |VTP|)^2 is also computed (condition branch in the note).
Small-signal transfer function is solved by nodal analysis, not by a gain formula.
"""
import sympy as sp

s = sp.symbols("s")
VT, ID, VSD, CL = sp.Rational(8, 10), sp.Rational(4, 10), 4, sp.Rational(10, 1)  # mA, V, pF
Kp = sp.Rational(1, 10)


def design(half):
    k = Kp / 2 if half else Kp
    VSG = VT + sp.sqrt(ID / k)
    VS, VD = VSG, VSG - VSD
    RS = (5 - VS) / ID      # k ohm (V / mA)
    RD = (VD + 5) / ID
    gm = 2 * k * (VSG - VT)  # mA/V
    # nodal small-signal: vg=vi=1, id flows source->drain, source node: -vs/RS = id, id = gm (vs - vi)
    vs_, vo = sp.symbols("vs vo")
    idd = gm * (vs_ - 1)
    sol = sp.solve([sp.Eq(-vs_ / RS, idd), sp.Eq(idd, vo * (1 / RD + s * CL * sp.Rational(1, 1000)))], [vs_, vo], dict=True)[0]
    H = sp.simplify(sol[vo])   # CL pF with RD in kOhm -> s*CL*1e-3 in ms^-1 ... time unit: microseconds
    return dict(VSG=VSG, RS=RS, RD=RD, gm=gm, H=H)


def close(x, y, tol=0.005):
    return abs(float(x) - y) / abs(y) <= tol


# primary convention
a = design(False)
assert a["VSG"] == sp.Rational(28, 10) and a["RS"] == sp.Rational(11, 2) and a["RD"] == sp.Rational(19, 2)
assert close(a["gm"], 0.4)
# check bias: ID = Kp (VSG - 0.8)^2 and KVL through RS, transistor, RD
assert Kp * (a["VSG"] - VT) ** 2 == ID and 5 - ID * a["RS"] - VSD - ID * a["RD"] + 5 == 0
A0 = a["H"].subs(s, 0)
assert close(A0, -1.1875)
# pole: den of H in s (units: s in 1/microsecond since CL[pF]*RD[kOhm] = ns, scaled by 1e-3 -> us)
num, den = sp.fraction(sp.together(a["H"]))
pole = sp.solve(den, s)[0]   # rad/us
tau = -1 / pole              # us
assert close(tau, 0.095, 1e-6)  # RD*CL = 9.5 kOhm * 10 pF = 95 ns
fc = float(1 / (2 * sp.pi * tau * 1e-6))
assert close(fc, 1.6755e6, 0.001)
gm_RS = a["gm"] * a["RS"]
assert gm_RS == sp.Rational(22, 10) and close(-a["gm"] * a["RD"] / (1 + gm_RS), -1.1875)

# alternative convention (1/2)Kp
b = design(True)
assert close(b["RS"], 3.4289, 0.001) and close(b["RD"], 11.5711, 0.001)
assert close(b["H"].subs(s, 0), -1.66144, 0.0001)
tau_b = -1 / sp.solve(sp.fraction(sp.together(b["H"]))[1], s)[0]
assert close(float(1 / (2 * sp.pi * tau_b * 1e-6)), 1.3755e6, 0.001)
print(f"Neamen: RS={float(a['RS'])} k RD={float(a['RD'])} k A0={float(A0):.4f} fc={fc/1e6:.4f} MHz | half-Kp: A0={float(b['H'].subs(s,0)):.5f}")
print("PASS EE-104-02-1")
