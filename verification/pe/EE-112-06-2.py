"""EE-112-06-2: demand, diversity and load factors (30-day month assumed)."""
from fractions import Fraction as F

eq = {1: (300, F(95,100), F(80,100), F(70,100)), 2: (250, F(85,100), F(60,100), F(60,100)),
      3: (500, F(80,100), F(50,100), F(40,100)), 4: (250, F(70,100), F(70,100), F(50,100))}
Pmax = {k: S*pf*df for k, (S, pf, df, lf) in eq.items()}
assert [float(Pmax[k]) for k in (1,2,3,4)] == [228.0, 127.5, 200.0, 122.5]
PA = (Pmax[1]+Pmax[2]) / F(12,10); PB = (Pmax[3]+Pmax[4]) / F(14,10)
Pm = (PA+PB) / F(115,100)
assert abs(float(PA)-296.25) < 1e-9 and abs(float(PB)-230.357) < 1e-3 and abs(float(Pm)-457.92) < 1e-2
Pavg = sum(Pmax[k]*eq[k][3] for k in eq)
assert float(Pavg) == 377.35
# independent: energy as sum of per-equipment daily energies
E = sum(Pmax[k]*eq[k][3]*24 for k in eq) * 30
assert float(E) == 271692.0
print("PASS EE-112-06-2")
