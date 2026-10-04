"""EE-106-05-4: single-phase transformer differential relay.

Currents (figure): I1 into primary, I2 out of secondary (ideal N1:N2),
I1' = I1/n1, I2' = I2/n2 (CT ratio 1/n), relay current I' = I1' - I2'.
"""
import sympy as sp

I1, N1, N2, n1, n2 = sp.symbols("I1 N1 N2 n1 n2", positive=True)
I2 = N1 / N2 * I1                        # ampere-turn balance of the ideal transformer
Ip = I1 / n1 - I2 / n2                   # (1) relay current
assert sp.simplify(Ip - I1 * (1 / n1 - N1 / (N2 * n2))) == 0
ratio = sp.solve(sp.Eq(Ip, 0), n1)[0]    # (2) condition for I' = 0
assert sp.simplify(ratio - n2 * N2 / N1) == 0
assert sp.simplify(ratio / n2 - N2 / N1) == 0    # n1/n2 = N2/N1
# (3) with the condition, I' = 0 for any load current
assert sp.simplify(Ip.subs(n1, ratio)) == 0
# numeric illustration: 22 kV/11 kV (N1/N2 = 2), CT2 n2 = 200 -> n1 = 100
num = {N1: 2, N2: 1, n2: 200}
assert ratio.subs(num) == 100
assert Ip.subs(num).subs(n1, 100).subs(I1, 50) == 0
# internal fault: I2 effectively reduced -> I' nonzero
assert (I1 / 100 - 0.8 * (2 * I1) / 200).subs(I1, 50) != 0
print("PASS EE-106-05-4")
