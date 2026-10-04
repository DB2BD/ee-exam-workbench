"""EE-104-05-2: three 200 MVA 161/69 kV transformers in parallel, load 320+j240 MVA at 69 kV.

z = (0.5+j10)%, (0.6+j12)%, (0.7+j14)% on 200 MVA; iron loss = 25 % of rated copper loss each;
overload limit 110 % = 220 MVA; magnetising current neglected.  Load voltage 1.0 pu.
"""
import itertools

import numpy as np


def close(a, b, tol=5e-3):
    assert abs(a - b) <= tol * max(abs(b), 1e-9), (a, b)


Sb = 200.0
z = np.array([0.005 + 0.10j, 0.006 + 0.12j, 0.007 + 0.14j])
SL = (320 + 240j) / Sb
Pcu_rated = z.real * Sb               # MW at rated current: 1.0, 1.2, 1.4
Pfe = 0.25 * Pcu_rated


def share(idx):
    """Current sharing with common voltage drop: I_i = I_L * (1/z_i) / sum(1/z)."""
    y = 1 / z[list(idx)]
    I_L = np.conj(SL) / 1.0
    I = I_L * y / y.sum()
    zeq = 1 / y.sum()
    return I, zeq


def loss(idx, I):
    return sum(abs(Ii) ** 2 * z[i].real * Sb + Pfe[i] for i, Ii in zip(idx, I))


# three in parallel
I3, zeq3 = share((0, 1, 2))
S3 = np.conj(I3) * Sb
close(abs(S3[0]), 157.009); close(abs(S3[1]), 130.841); close(abs(S3[2]), 112.150)
E161 = 1.0 + zeq3 * np.conj(SL)       # V_high = V_load + zeq * I_L
close(abs(E161) * 161, 169.369, 1e-3)
close(abs(E161), 1.051981, 1e-4)
close(loss((0, 1, 2), I3), 2.4701, 1e-3)
Pl = [abs(I3[i]) ** 2 * z[i].real * Sb + Pfe[i] for i in range(3)]
close(Pl[0], 0.86630, 1e-3); close(Pl[1], 0.81358, 1e-3); close(Pl[2], 0.79021, 1e-3)

# two in parallel
out = {}
for idx in itertools.combinations(range(3), 2):
    I, _ = share(idx)
    mva = np.abs(I) * Sb
    out[idx] = (mva, loss(idx, I), bool((mva <= 220).all()))
assert out[(0, 2)][2] is False and out[(0, 1)][2] and out[(1, 2)][2]
close(out[(0, 2)][0][0], 233.333)
close(out[(0, 1)][0][0], 218.182); close(out[(0, 1)][0][1], 181.818)
close(out[(1, 2)][0][0], 215.385)
close(out[(0, 1)][1], 2.73182, 1e-4)
close(out[(0, 2)][1], 2.93333, 1e-3)
close(out[(1, 2)][1], 3.23462, 1e-3)
allowed = {k: v[1] for k, v in out.items() if v[2]}
assert min(allowed, key=allowed.get) == (0, 1)

# complex power of the best pair and per-unit loss
I, _ = share((0, 1))
Sbest = np.conj(I) * Sb
close(Sbest[0].real, 174.545); close(Sbest[0].imag, 130.909)
close(Sbest[1].real, 145.455); close(Sbest[1].imag, 109.091)
close(abs(I[0]) ** 2 * z[0].real * Sb + Pfe[0], 1.44008, 1e-3)
close(abs(I[1]) ** 2 * z[1].real * Sb + Pfe[1], 1.29174, 1e-3)
# independent: total complex power balance S_in = S_L + z_i |I_i|^2 (series part), real part = copper loss
Pcu = sum(abs(Ii) ** 2 * zi.real for Ii, zi in zip(I, z[[0, 1]])) * Sb
close(Pcu, 1.19008 + 0.99174, 1e-3)
print("PASS EE-104-05-2")
