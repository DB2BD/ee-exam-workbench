"""EE-108-04-2: separately excited DC motor 125 V back-emf at 3000 rpm, Ra = 0.03 ohm, Vt = 128 V."""
import math
Vt, Ea, Ra, n = 128.0, 125.0, 0.03, 3000.0
Ia = (Vt - Ea) / Ra
Pin = Vt * Ia
Pem = Ea * Ia
w = 2 * math.pi * n / 60
Tem = Pem / w
assert abs(Ia - 100) < 1e-9
assert abs(Pin - 12800) < 1e-6 and abs(Pem - 12500) < 1e-6
assert abs(Tem - 39.79) / 39.79 <= 0.005
# independent: power balance and torque from machine constant
assert abs(Pin - Ia**2 * Ra - Pem) < 1e-9
Kphi = Ea / w
assert abs(Kphi * Ia - Tem) < 1e-9
print(f"Ia={Ia} Pin={Pin} Pem={Pem} Tem={Tem:.4f}")
print("PASS EE-108-04-2")
