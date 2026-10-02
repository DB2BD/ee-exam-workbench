"""EE-114-05-5 independent check: swing equation after load rejection.

Givens (official crop): 2 poles, 60 Hz, 250 MVA, H = 4.32 s, 60 MW = 0.24 pu,
load suddenly removed; constant acceleration for 12 cycles.
"""
import sympy as sp

H, f, P = sp.Rational(432, 100), 60, sp.Rational(24, 100)
ws = 2 * sp.pi * f
# Method 1: (2H/ws) d2delta/dt2 = Pa, Pa = Pm - 0 = 0.24.
alpha = ws * P / (2 * H)
assert sp.simplify(alpha - 10 * sp.pi / 3) == 0
t = sp.Rational(12, 60)
Ns = 120 * f / 2
N_end = Ns + alpha * t * 60 / (2 * sp.pi)  # 2-pole: electrical = mechanical rad
assert sp.simplify(N_end - 3620) == 0

# Method 2: energy approach. Kinetic energy W = H*S at synchronous speed;
# accelerating power 60 MW for 0.2 s raises W: (N/Ns)^2 = 1 + Pa t/(H) (linearised).
W0 = H * 250  # MJ
W1 = W0 + 60 * t  # MJ
N_energy = Ns * sp.sqrt(W1 / W0)
assert abs(float(N_energy) - 3620) / 3620 <= 0.005
assert abs(float(alpha) - 10.472) / 10.472 <= 0.005
print("PASS EE-114-05-5")
