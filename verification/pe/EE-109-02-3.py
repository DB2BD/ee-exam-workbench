"""EE-109-02-3 independent check: flyback converter, Np/Ns = 4.

Givens (official crop): RL = 0.8 ohm, Vo = 24 V, Vd = 0.7 V, Vt = 1.2 V, f = 1.5 kHz, D = 0.75,
lossless transformer, load-current ripple neglected.  Vs is not given.
Method:
  * average-current balance (mode independent): (Vs - Vt) Ip_avg = (Vo + Vd) Io and
    secondary volt-second balance give Vs, Ip_avg (full period) and eta;
  * reference-book branch: magnetising current starting from zero (DCM / CrCM boundary):
    secondary triangle average over (1-D)T equals Io -> Ip_max; Lp from the primary slope,
    cross-checked by energy per cycle and by the demagnetising time.
"""
import sympy as sp


def close(x, y):
    return abs(float(x) - y) / abs(y) <= 0.005


n, RL, Vo, Vd, Vt, f, D = 4, sp.Rational(8, 10), 24, sp.Rational(7, 10), sp.Rational(6, 5), 1500, sp.Rational(3, 4)
T = sp.Rational(1, f)
Io = Vo / RL
Po = Vo * Io
Vs = sp.symbols("Vs", positive=True)
# primary volt-second balance: (Vs - Vt) D = n (Vo + Vd)(1 - D)  (CCM or boundary)
Vs = sp.solve(sp.Eq((Vs - Vt) * D, n * (Vo + Vd) * (1 - D)), Vs)[0]
Ip_avg = (Vo + Vd) * Io / (Vs - Vt)          # full-period average switch current
eta = Po / (Vs * Ip_avg)

# boundary branch: secondary current triangle from Is_max to 0 during (1-D)T
Is_max = 2 * Io / (1 - D)
Ip_max = Is_max / n
Ip_on = Ip_max / 2                           # average over the on-interval only
Lp = (Vs - Vt) * D * T / Ip_max              # primary slope
assert sp.simplify(sp.Rational(1, 2) * Lp * Ip_max**2 * f - (Vo + Vd) * Io) == 0   # energy per cycle
t_demag = Lp * Ip_max / (n * (Vo + Vd))
assert sp.simplify(t_demag - (1 - D) * T) == 0   # exactly the CrCM boundary
assert sp.simplify(Ip_avg - D * Ip_on) == 0

assert close(Io, 30) and close(Vs, 34.1333)
assert close(Ip_max, 60) and close(Ip_on, 30) and close(Ip_avg, 22.5)
assert close(Lp * 1e6, 274.4) and close(eta * 100, 93.75)
assert close(t_demag * 1e6, 166.67)
print(f"Vs={float(Vs):.4f} V Ip_max={Ip_max} A Ip_avg={Ip_avg} A (on-interval {Ip_on} A) "
      f"Lp={float(Lp)*1e6:.2f} uH eta={float(eta)*100:.2f}% t_demag={float(t_demag)*1e6:.2f} us")
print("PASS EE-109-02-3")
