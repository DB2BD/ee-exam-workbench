"""EE-112-03-4 independent check: harmonic conjugate of u = e^{-x}(x sin y - y cos y)."""
import sympy as sp

x, y = sp.symbols("x y", real=True)
u = sp.exp(-x) * (x * sp.sin(y) - y * sp.cos(y))
assert sp.simplify(u.diff(x, 2) + u.diff(y, 2)) == 0  # harmonic

# Method 1: integrate Cauchy-Riemann v_y = u_x, then fix g(x) with v_x = -u_y.
v0 = sp.integrate(u.diff(x), y)
gprime = sp.simplify(-u.diff(y) - v0.diff(x))
assert gprime == 0
v = sp.simplify(v0)
target = sp.exp(-x) * (x * sp.cos(y) + y * sp.sin(y))
assert sp.simplify(v - target) == 0

# Method 2: f(z) = i z e^{-z} has real part u and imaginary part v.
f = sp.expand_complex(sp.I * (x + sp.I * y) * sp.exp(-(x + sp.I * y)))
assert sp.simplify(sp.re(f) - u) == 0 and sp.simplify(sp.im(f) - target) == 0
print("PASS EE-112-03-4")
