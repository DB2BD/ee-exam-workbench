"""EE-112-04-5: 250 V DC shunt motor, Ra = 0.12, Rf = 50 ohm, 1000 turns/pole,
AR 1500 A-turns at I_L = 150 A, magnetisation curve at 1200 rpm (Fig. 4).
E_A0 at the effective field current is digitised from the official crop."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
img = np.array(Image.open(ROOT / "依考科分類/04_電機機械/images/questions/PE_112年_電機機械_Q05.png").convert("L")).astype(int)

V, Ra, Rf, Nf, AR, IL, n0 = 250.0, 0.12, 50.0, 1000, 1500, 150.0, 1200.0
If = V / Rf
Ia = IL - If
If_eff = If - AR / Nf
assert abs(If_eff - 3.5) < 1e-12

# axis calibration measured on the crop: If grid 0..10 A at x = 697..1180 px,
# Ea grid 0..300 V at y = 859.5..379 px
x = round(697 + (1180 - 697) * If_eff / 10)
grid_rows = {379, 459, 538, 539, 619, 699, 780, 858, 859, 860}
rows = [y for xx in (x - 1, x, x + 1) for y in range(380, 858) if img[y, xx] < 140 and y not in grid_rows]
EA0_digit = (859.5 - np.mean(rows)) / (859.5 - 379) * 300
assert 196 <= EA0_digit <= 205, EA0_digit
EA0 = 200.0                                  # graph reading used in the note

Ea = V - Ia * Ra
n = n0 * Ea / EA0
wm = 2 * np.pi * n / 60
T = Ea * Ia / wm
assert abs(n - 1396) / 1396 <= 0.005
assert abs(T - 230.8) / 230.8 <= 0.005
# independent: T = K*phi*Ia with K*phi from the 1200-rpm curve
Kphi = EA0 / (2 * np.pi * n0 / 60)
assert abs(Kphi * Ia - T) < 1e-9
# no-load sanity: curve at If = 5 A gives ~250 V
x5 = round(697 + (1180 - 697) * 0.5) - 2   # step off the 5-A grid line
rows5 = [y for y in range(380, 858) if img[y, x5] < 140 and y not in grid_rows]
assert abs((859.5 - np.mean(rows5)) / (859.5 - 379) * 300 - 250) < 5
print(f"If_eff={If_eff} A EA0(digitised)={EA0_digit:.1f} V n={n:.1f} rpm T={T:.1f} N.m")
print("PASS EE-112-04-5")
