"""EE-108-04-4: 3-phase Y, 2300 V, 1500 kW, 60 Hz, 30-pole cylindrical synchronous motor, Xs = 1.95 ohm/phase,
lossless, infinite bus, rated load at unity input power factor."""
import numpy as np

VL, P, f, poles, Xs = 2300.0, 1.5e6, 60.0, 30, 1.95
Vph = VL / np.sqrt(3)
Ia = P / (np.sqrt(3) * VL)                  # unity pf, losses neglected
Ef = Vph - 1j * Xs * Ia                      # motor convention V = E + jXs I
E_LL = np.sqrt(3) * abs(Ef)
delta = np.degrees(np.angle(Ef))
Pmax = 3 * Vph * abs(Ef) / Xs
ws = 2 * np.pi * (120 * f / poles) / 60
Tmax = Pmax / ws
assert abs(E_LL - 2628.18) / 2628.18 <= 0.005
assert abs(Pmax - 3.0999e6) / 3.0999e6 <= 0.005
assert abs(Tmax - 1.2334e5) / 1.2334e5 <= 0.005
assert abs(delta + 28.94) < 0.01
# independent: rated power from the angle characteristic must equal 1.5 MW
assert abs(3 * Vph * abs(Ef) / Xs * np.sin(np.radians(-delta)) - P) < 1e-3
# independent: scan delta, maximum is at 90 deg
d = np.radians(np.linspace(0, 180, 18001))
p = 3 * Vph * abs(Ef) / Xs * np.sin(d)
assert abs(np.degrees(d[p.argmax()]) - 90) < 0.01
print(f"Ia={Ia:.4f} Ef={abs(Ef):.3f} E_LL={E_LL:.2f} delta={delta:.3f} Pmax={Pmax:.1f} ws={ws:.4f} Tmax={Tmax:.1f}")
print("PASS EE-108-04-4")
