"""EE-113-03-4 independent check: Lyapunov equation PA + A^T P = -I, A = [[0,1],[-5,-6]]."""
import numpy as np
import sympy as sp

p1, p2, p3, lam = sp.symbols("p1 p2 p3 lam")
A = sp.Matrix([[0, 1], [-5, -6]])
P = sp.Matrix([[p1, p2], [p2, p3]])
sol = sp.solve(list(P * A + A.T * P + sp.eye(2)), [p1, p2, p3], dict=True)[0]
Ps = P.subs(sol)
assert Ps == sp.Matrix([[sp.Rational(11, 10), sp.Rational(1, 10)], [sp.Rational(1, 10), sp.Rational(1, 10)]])
ev = sp.solve(sp.det(Ps - lam * sp.eye(2)), lam)
assert {sp.nsimplify(e) for e in ev} == {(6 + sp.sqrt(26)) / 10, (6 - sp.sqrt(26)) / 10}
assert all(abs(a - b) < 1e-12 for a, b in zip(sorted(float(e) for e in ev), [(6 - 26**0.5) / 10, (6 + 26**0.5) / 10]))

# Independent: Kronecker-vectorised linear solve (I(x)A^T + A^T(x)I) vec(P) = -vec(I), then eigvalsh.
An = np.array([[0.0, 1.0], [-5.0, -6.0]])
K = np.kron(np.eye(2), An.T) + np.kron(An.T, np.eye(2))
X = np.linalg.solve(K, -np.eye(2).reshape(-1, order="F")).reshape(2, 2, order="F")
assert np.allclose(X, [[1.1, 0.1], [0.1, 0.1]])
assert np.allclose(np.linalg.eigvalsh(X), [0.0900980486, 1.1099019514])
# trace / det cross-check
assert abs(X.trace() - 1.2) < 1e-12 and abs(np.linalg.det(X) - 0.1) < 1e-12
print("PASS EE-113-03-4")
