"""EE-104-04-3: PM DC motor, Ra=0.05 ohm, no mechanical loss. (3.0 V, 2.0 A, 600 rpm); then 3.1 V, constant torque, 612 rpm quoted."""
Ra = 0.05
V1, I1, n1 = 3.0, 2.0, 600.0
Ea1 = V1 - I1 * Ra
Pout1 = Ea1 * I1
assert abs(Pout1 - 5.8) / 5.8 < 0.005
# constant torque and constant PM flux -> T = K*I  -> I2 = I1
I2 = I1
V2 = 3.1
Ea2 = V2 - I2 * Ra
Pout2, Pin2 = Ea2 * I2, V2 * I2
eta2 = Pout2 / Pin2
assert abs(I2 - 2.0) < 1e-12
assert abs(eta2 - 0.967742) / 0.967742 < 0.005
# speed implied by constant-flux: n2 = n1*Ea2/Ea1 = 620.7 rpm (differs from the quoted 612 rpm)
n2_theory = n1 * Ea2 / Ea1
assert abs(n2_theory - 620.69) / 620.69 < 0.005
# if instead the quoted 612 rpm is enforced with Ea ~ n: Ia = (3.1 - Ea1*612/600)/Ra
Ia_612 = (V2 - Ea1 * 612 / n1) / Ra
assert abs(Ia_612 - 2.84) / 2.84 < 0.005
print("PASS EE-104-04-3")
