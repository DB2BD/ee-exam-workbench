"""EE-113-02-2 independent check: common-base BJT (T model), Rin and Av = vo/vsig.

Givens (official crop): alpha = 0.99, IE = 0.5 mA (ideal current source), Rsig = 75 ohm,
RC = RL = 12k, C1, C2 infinite, base grounded. VT is not given: main branch 25 mV
(reference-book convention), sensitivity at 25.85 mV and 26 mV.
Method: nodal solve of the T model with a test source; cross-check with
current-division closed form.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


def solve(VT):
    alpha, IE, Rsig, RC, RL = sp.Rational(99, 100), sp.Rational(1, 2000), 75, 12000, 12000
    re = VT / IE
    ve, vo = sp.symbols("ve vo")
    # T model: re from emitter to base (AC ground). i_re = current entering the emitter
    # terminal; the collector then draws -alpha*i_re, so the loads carry +alpha*i_re.
    i_re = ve / re
    eqs = [sp.Eq((1 - ve) / Rsig, i_re),            # emitter KCL (bias source is AC open), vsig = 1
           sp.Eq(vo / RC + vo / RL, alpha * i_re)]  # collector KCL
    sol = sp.solve(eqs, [ve, vo], dict=True)[0]
    Rin = re
    return float(Rin), float(sol[vo])


Rin, Av = solve(sp.Rational(25, 1000))
assert close(Rin, 50.0) and close(Av, 47.52)
# closed-form current division (different route)
assert close(0.99 * 6000 / (75 + 50), Av)
Rin2, Av2 = solve(sp.Rational(2585, 100000))
assert close(Rin2, 51.70) and close(Av2, 46.882399)
Rin3, Av3 = solve(sp.Rational(26, 1000))
assert close(Rin3, 52.0) and close(Av3, 46.771654)
print(f"VT=25mV Rin={Rin} Av={Av:.4f}; 25.85mV Av={Av2:.6f}; 26mV Av={Av3:.6f}")
print("PASS EE-113-02-2")
