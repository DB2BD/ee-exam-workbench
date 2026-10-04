"""EE-111-03-4 independent check: singular values of [[1,1],[1,3]], extrema of x^T A x on unit circle."""
import numpy as np
import sympy as sp

A = np.array([[1.0, 1.0], [1.0, 3.0]])
sv = np.linalg.svd(A, compute_uv=False)
assert np.allclose(sorted(sv), [2 - np.sqrt(2), 2 + np.sqrt(2)])
# sigma^2 = eig(A^T A) symbolically
As = sp.Matrix([[1, 1], [1, 3]])
ev = sorted((As.T * As).eigenvals().keys(), key=lambda e: float(e))
assert sp.simplify(sp.sqrt(ev[0]) - (2 - sp.sqrt(2))) == 0
assert sp.simplify(sp.sqrt(ev[1]) - (2 + sp.sqrt(2))) == 0
# Independent: parametrize x = (cos t, sin t)
th = np.linspace(0, 2 * np.pi, 200001)
q = np.cos(th) ** 2 + 2 * np.cos(th) * np.sin(th) + 3 * np.sin(th) ** 2
assert abs(q.min() - (2 - np.sqrt(2))) < 1e-8 and abs(q.max() - (2 + np.sqrt(2))) < 1e-8
print("PASS EE-111-03-4")
