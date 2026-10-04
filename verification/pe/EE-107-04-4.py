"""EE-107-04-4: 3-phase Y, 6-pole synchronous generator 380 V, 100 kVA, 60 Hz, Xs = 0.1 ohm, Ra = 0.
Friction+windage 3 kW, core loss 2 kW, no copper/stray/field loss counted.  Full load pf 0.8 lagging at 380 V."""
import numpy as np

VL, S, Xs, pf = 380.0, 100e3, 0.1, 0.8
Vph = VL / np.sqrt(3)
Ia = S / (np.sqrt(3) * VL)
I = Ia * (pf - 1j * np.sqrt(1 - pf**2))               # lagging
E = Vph + 1j * Xs * I
V0 = np.sqrt(3) * abs(E)
Pout = S * pf
Pin = Pout + 3e3 + 2e3
eta = Pout / Pin
assert abs(V0 - 396.35) / 396.35 <= 0.005
assert abs(eta - 0.9412) / 0.9412 <= 0.005
# independent: E^2 = (V + Xs*Ia*sin)^2 + (Xs*Ia*cos)^2 (scalar formula)
E2 = np.hypot(Vph + Xs * Ia * np.sqrt(1 - pf**2), Xs * Ia * pf)
assert abs(E2 - abs(E)) < 1e-9
# independent: power-angle check, P = 3*V*E*sin(delta)/Xs must reproduce the 80 kW output
delta = np.angle(E)
assert abs(3 * Vph * abs(E) * np.sin(delta) / Xs - Pout) < 1e-6
print(f"Ia={Ia:.3f} E={abs(E):.4f} V0={V0:.3f} eta={eta:.5f} VR={(V0-VL)/VL*100:.2f}%")
print("PASS EE-107-04-4")
