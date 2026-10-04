"""EE-108-05-4: generator-winding differential protection (descriptive question).

Quantitative arguments (percentage differential, operating coil 3 = I1 - I2,
restraining coils 1 and 2): zero operating current for through faults, large for
internal faults, and a slope setting that tolerates CT mismatch.
"""
SLOPE = 0.20  # example percentage-differential slope


def trips(i1, i2, slope=SLOPE):
    iop = abs(i1 - i2)
    irt = (abs(i1) + abs(i2)) / 2
    return iop > slope * irt, iop, irt


# normal load / external fault: current enters one end and leaves the other (I1 = I2)
t, iop, irt = trips(5.0, 5.0)
assert not t and iop == 0.0
# external fault with 5 % CT mismatch: still restrained
t, iop, irt = trips(10.0, 9.5)
assert not t and abs(iop / irt - 0.5 / 9.75) < 1e-12 and iop / irt < SLOPE
# internal fault fed from one end only: I2' = 0
t, iop, irt = trips(10.0, 0.0)
assert t and abs(iop - 10.0) < 1e-12 and abs(irt - 5.0) < 1e-12
# internal fault fed from both ends: both currents flow into the fault, I2 reverses sign
t, iop, irt = trips(6.0, -4.0)
assert t and abs(iop - 10.0) < 1e-12 and abs(irt - 5.0) < 1e-12
# KCL on the protected zone: I1' = I2' + If'  => (I1 - I2) proportional to If'
i2p, ifp = 4.0, 6.0
i1p = i2p + ifp  # I1' = I2' + If'
assert abs((i1p - i2p) - ifp) < 1e-12
print("PASS EE-108-05-4 (descriptive)")
