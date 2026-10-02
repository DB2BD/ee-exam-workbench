"""EE-114-04-2: tap-changing transformer, maximum power to a resistive load.

Givens: source 110*sqrt(2) V with internal impedance j1 ohm, R_L = 2.5 ohm,
a = N1/N2 adjustable.  Branches: label read as RMS (main) or as peak.
"""
import numpy as np

Zs, RL = 1j * 1.0, 2.5
# brute-force search over a for max load power (independent of |Zs| rule)
a_grid = np.linspace(0.3, 1.2, 900001)
Rp = a_grid**2 * RL
P = (np.abs(1.0 / (Zs + Rp)) ** 2) * Rp      # per unit V^2
a_opt = a_grid[np.argmax(P)]
assert abs(a_opt - 0.632456) / 0.632456 <= 0.005

def Vo(Vs_rms, a):
    I1 = Vs_rms / (Zs + a**2 * RL)
    V1 = I1 * a**2 * RL
    return abs(V1) / a

a = np.sqrt(1 / RL)
vo_rms = Vo(110 * np.sqrt(2), a)            # label is RMS
vo_pk = Vo(110.0, a)                        # label is the peak value
assert abs(vo_rms - 173.925) / 173.925 <= 0.005
assert abs(vo_pk - 122.984) / 122.984 <= 0.005
# power check: Vo^2/RL equals primary-side power |I1|^2 * 1 ohm
I1 = abs(110 * np.sqrt(2) / (Zs + 1.0))
assert abs(vo_rms**2 / RL - I1**2 * 1.0) < 1e-6
print(f"a={a:.6f} Vo(rms label)={vo_rms:.3f} V Vo(peak label)={vo_pk:.3f} V")
print("PASS EE-114-04-2")
