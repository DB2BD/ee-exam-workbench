"""EE-107-04-2: series DC motor, Vt = 50 V, R_AS = 0.05 ohm.  Magnetisation curve at 1200 rpm:
Ea0 = 40 V at Ia = 10 A and 48 V at Ia = 200 A.  Np = 25 is not needed (curve given)."""
import math
Vt, R, n0 = 50.0, 0.05, 1200.0
pts = {10.0: 40.0, 200.0: 48.0}
expect = {10.0: (1485.0, 3.183), 200.0: (1000.0, 76.394)}
for Ia, Ea0 in pts.items():
    Ea = Vt - Ia * R
    n = n0 * Ea / Ea0                                  # same flux => Ea proportional to speed
    w = 2 * math.pi * n / 60
    T = Ea * Ia / w
    assert abs(n - expect[Ia][0]) / expect[Ia][0] <= 0.005
    assert abs(T - expect[Ia][1]) / expect[Ia][1] <= 0.005
    # independent: torque from the curve itself, T = Ea0*Ia/w0 (flux-only quantity)
    T2 = Ea0 * Ia / (2 * math.pi * n0 / 60)
    assert abs(T - T2) < 1e-9
    print(f"Ia={Ia} Ea={Ea} n={n:.3f} T={T:.4f}")
print("PASS EE-107-04-2")
