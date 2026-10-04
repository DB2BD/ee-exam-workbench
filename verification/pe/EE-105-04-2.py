"""EE-105-04-2: 120/240 V, 12 kVA transformer, 110 V on the 240 V winding."""
Vh, Vl, S = 240.0, 120.0, 12000.0
Vin = 110.0
a = Vh / Vl
Vout = Vin / a
Ih_rated, Il_rated = S / Vh, S / Vl
S_max = Vin * Ih_rated                      # winding current limited
assert abs(Vout - 55.0) / 55.0 < 0.005
assert abs(S_max - 5500.0) / 5500.0 < 0.005
assert abs(Vout * Il_rated - S_max) < 1e-6  # low-side route gives same value
# flux check: V/f ratio vs rated (flux proportional)
assert abs(Vin / Vh - Vout / Vl) < 1e-12
print("PASS EE-105-04-2")
