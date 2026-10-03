"""EE-106-04-1: C-core electromagnet, N = 400, R = 5 ohm, square pole 5 cm x 5 cm, two air gaps g = 0.1 cm,
iron reluctance neglected, average pull F = 550 N at g = 0.1 cm (stem prints N-m; a force is meant), DC supply."""
import math
N, R, a, g, F = 400, 5.0, 0.05, 1e-3, 550.0
mu0 = 4e-7 * math.pi
A = a * a
# force from field energy: two gaps, each B^2 A /(2 mu0)
B = math.sqrt(F * mu0 / A)
I = B * 2 * g / (mu0 * N)
V = I * R
W = 2 * B**2 / (2 * mu0) * A * g
assert abs(B - 0.5258) / 0.5258 <= 0.005
assert abs(I - 2.092) / 2.092 <= 0.005
assert abs(V - 10.46) / 10.46 <= 0.005
assert abs(W - 0.55) / 0.55 <= 0.005
# independent: inductance route, L = mu0 N^2 A / (2 g), F = (1/2) I^2 |dL/dg| = I^2 L / (2 g)
L = mu0 * N**2 * A / (2 * g)
assert abs(0.5 * L * I**2 - W) < 1e-9
assert abs(I**2 * L / (2 * g) - F) / F < 1e-9
# flux linkage: lambda = L I = N B A
assert abs(L * I - N * B * A) < 1e-9
print(f"B={B:.4f} I={I:.4f} V={V:.3f} L={L:.4f} W={W:.4f}")
print("PASS EE-106-04-1")
