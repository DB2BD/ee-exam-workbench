"""EE-113-05-2 independent check: transient fault currents at generator terminal.

Givens (official crop): 100 MVA, 24 kV base; generator X' = 0.25, line X = 0.1,
motor X' = 0.2 pu; motor terminal 20 kV, absorbs 50 MW at pf 0.8 leading;
three-phase fault at generator terminal.
"""
import numpy as np

close = lambda a, b: abs(a - b) <= 0.005 * abs(b)
Vm = 20 / 24
S = 0.5 - 0.375j  # leading pf: Q absorbed < 0
I = np.conj(S / Vm)  # current from generator toward motor

# Method 1: internal EMFs, each branch shorted at the fault point.
Eg = Vm + 1j * (0.1 + 0.25) * I
Em = Vm - 0.2j * I
Ig = Eg / 0.25j
Im = Em / (0.2j + 0.1j)  # motor contribution flowing toward fault
If = Ig + Im
IB = 100e6 / (np.sqrt(3) * 24e3)
assert close(I, 0.6 + 0.45j)
assert close(Ig, 0.84 - 2.70333j) and close(abs(Ig), 2.8308)
assert close(Im, -0.4 - 3.07778j) and close(abs(Im), 3.1037)
assert close(If, 0.44 - 5.78111j) and close(abs(If), 5.7978)
assert close(abs(Ig) * IB, 6809.9) and close(abs(Im) * IB, 7466.3) and close(abs(If) * IB, 13947.4)

# Method 2: Thevenin + superposition at the fault bus.
Vf = Vm + 0.1j * I
Zth = 1 / (1 / 0.25j + 1 / 0.3j)
If2 = Vf / Zth
assert close(If2, If)
# Generator current = prefault load current (-I leaving the gen toward fault is +I out of gen)
Ig2 = I + If2 * (0.3 / 0.55)
Im2 = -I + If2 * (0.25 / 0.55)
assert close(Ig2, Ig) and close(Im2, Im)
print("PASS EE-113-05-2")
