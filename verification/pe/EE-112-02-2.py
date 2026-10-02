"""EE-112-02-2 independent check: op-amp Schmitt relaxation oscillator.

Givens (official crop): R1 = 10k (v+ to ground), R2 = 20k (vo to v+), RX = 40k (vo to vX),
CX = 0.02 uF (vX to ground), vo = +/-5 V; vX on the inverting input; at t = 0 vo has
just switched high.
Method: event-driven numerical integration of dvX/dt = (vo - vX)/(RX CX) with the
comparator rule, versus the closed-form waveform in the note.
"""
import math


def close(x, y):
    return abs(x - y) / abs(y) <= 0.005


R1, R2, RX, CX, Vsat = 10e3, 20e3, 40e3, 0.02e-6, 5.0
beta = R1 / (R1 + R2)
VTH = beta * Vsat
tau = RX * CX
# closed forms
tH = tau * math.log((Vsat + VTH) / (Vsat - VTH))
T = 2 * tH
f = 1 / T
assert close(tau, 0.8e-3) and close(tH, 0.554518e-3) and close(f, 901.684)

# event-driven simulation (exact exponential steps)
dt = 1e-8
vx, vo, t = -VTH, Vsat, 0.0
switches = []
a = math.exp(-dt / tau)
while len(switches) < 5:
    vx = vo + (vx - vo) * a
    t += dt
    if vo > 0 and vx >= beta * vo:
        vo = -Vsat
        switches.append(t)
    elif vo < 0 and vx <= beta * vo:
        vo = Vsat
        switches.append(t)
highs = [switches[0]] + [switches[k] - switches[k - 1] for k in (2, 4)]
lows = [switches[k] - switches[k - 1] for k in (1, 3)]
Tsim = switches[2] - switches[0]
assert close(1 / Tsim, f)
assert close(sum(highs) / 3 / Tsim, 0.5)
assert all(close(h, tH) for h in highs) and all(close(l, tH) for l in lows)
# waveform formula check at a sample point
t_s = 0.3e-3
assert close(5 - 20 / 3 * math.exp(-t_s / tau), Vsat + (-VTH - Vsat) * math.exp(-t_s / tau))
print(f"tau={tau*1e3} ms tH={tH*1e3:.6f} ms f={f:.3f} Hz duty=50%; sim f={1/Tsim:.2f}")
print("PASS EE-112-02-2")
