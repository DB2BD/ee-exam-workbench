"""EE-111-04-5: 2300 V plant, 3000 kW at 0.85 lag; synchronous condenser Xs = 1.6 ohm to pf 1."""
import numpy as np

VL, P, pf, Xs = 2300.0, 3000e3, 0.85, 1.6
Q = P * np.tan(np.arccos(pf))
assert abs(Q / 1e3 - 1859.2) / 1859.2 <= 0.005
I_before = P / (np.sqrt(3) * VL * pf)
I_after = P / (np.sqrt(3) * VL)
assert abs(I_before - 885.96) / 885.96 <= 0.005
assert abs(I_after - 753.07) / 753.07 <= 0.005
assert abs((I_before - I_after) - 132.89) / 132.89 <= 0.005
# condenser: motor convention, current leads V by 90 deg
Vph = VL / np.sqrt(3)
Ic = 1j * Q / (np.sqrt(3) * VL)
Ef = Vph - 1j * Xs * Ic
assert abs(Ef.imag) < 1e-9
assert abs(abs(Ef) - 2074.6) / 2074.6 <= 0.005
assert abs(np.sqrt(3) * abs(Ef) - 3593.4) / 3593.4 <= 0.005
# independent: KCL at the plant bus, load current + condenser current is in phase with V
Iload = I_before * np.exp(-1j * np.arccos(pf))
Itot = Iload + Ic
assert abs(np.angle(Itot)) < 1e-9 and abs(abs(Itot) - I_after) < 1e-6
# condenser reactive output from its own phasors: Q = 3 V (E - V) / Xs
assert abs(3 * Vph * (abs(Ef) - Vph) / Xs - Q) / Q < 1e-9
print(f"Q={Q/1e3:.2f} kvar I={I_before:.2f}->{I_after:.2f} A Ef={abs(Ef):.2f} V/ph {np.sqrt(3)*abs(Ef):.1f} V LL")
print("PASS EE-111-04-5")
