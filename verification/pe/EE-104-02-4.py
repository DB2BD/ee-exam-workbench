"""EE-104-02-4 independent check: single-phase full-bridge inverter, square-wave vo, RL load.

Givens (official crop): f = 100 Hz, Vdc = 100 V, R = 10 ohm, L = 20 mH.  Output +Vdc during the
first half period (assumed start), -Vdc during the second.
Method: RK4 integration of L di/dt = vo - R i over many periods until periodic steady state;
compare with the closed-form half-cycle expressions.
"""
import numpy as np

Vdc, R, L, f = 100.0, 10.0, 20e-3, 100.0
T = 1 / f
dt = T / 20000


def vo(t):
    return Vdc if (t % T) < T / 2 else -Vdc


def step(i, t):
    k1 = (vo(t) - R * i) / L
    k2 = (vo(t + dt / 2) - R * (i + dt / 2 * k1)) / L
    k3 = (vo(t + dt / 2) - R * (i + dt / 2 * k2)) / L
    k4 = (vo(t + dt) - R * (i + dt * k3)) / L
    return i + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


i, t = 0.0, 0.0
for _ in range(60 * 20000):      # 60 periods >> tau = 2 ms
    i, t = step(i, t), t + dt
hist = []
for _ in range(20000):
    hist.append(i)
    i, t = step(i, t), t + dt
hist = np.array(hist)
tt = np.arange(20000) * dt


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


tau = L / R
Imax = Vdc / R * (1 - np.exp(-T / 2 / tau)) / (1 + np.exp(-T / 2 / tau))
assert close(Imax, 8.483, 0.001) and close(tau, 2e-3)
assert close(hist.max(), Imax, 0.001) and close(hist.min(), -Imax, 0.001) and abs(hist[0] + Imax) < 0.01
A = Imax + Vdc / R
assert close(A, 18.483, 0.001)
closed = np.where(tt < T / 2, 10 - A * np.exp(-tt / tau), -10 + A * np.exp(-(tt - T / 2) / tau))
assert np.max(np.abs(closed - hist)) < 0.005
print(f"Imax={Imax:.4f} A, A={A:.4f}, max |closed - RK4| = {np.max(np.abs(closed-hist)):.2e}")
print("PASS EE-104-02-4")
