"""EE-105-05-5: penalty factor / incremental loss ranking from IC_i = 10, 9, 11 $/MWh.

Loss-coordination condition: lambda = IC_i * L_i, L_i = 1/(1 - ITL_i), ITL_i = dPL/dP_i.
lambda is not given; the ranking must hold for every lambda > max(IC_i) (so that ITL_i in (0,1)).
"""
import numpy as np

IC = np.array([10.0, 9.0, 11.0])

for lam in np.linspace(11.01, 200, 500):
    L = lam / IC
    ITL = 1 - 1 / L
    assert int(np.argmax(L)) == 1 and int(np.argmax(ITL)) == 1
    assert np.all(ITL > 0) and np.all(ITL < 1)
    assert np.allclose(ITL, 1 - IC / lam)

# pairwise difference sign, independent of lambda: L2 - L1 = lam (1/9 - 1/10) > 0
assert 1 / 9 - 1 / 10 > 0 and 1 / 9 - 1 / 11 > 0 and 1 / 10 - 1 / 11 > 0
print("PASS EE-105-05-5")
