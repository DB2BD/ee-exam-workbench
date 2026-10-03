"""EE-107-03-3 independent check (official crop): F=(4xz, xyz^2, 3y), cone x^2+y^2=z^2, 0<=z<=2."""
import sympy as sp

x, y, z, r, th = sp.symbols("x y z r theta", real=True)
F = sp.Matrix([4 * x * z, x * y * z**2, 3 * y])
div = sum(F[i].diff(v) for i, v in enumerate((x, y, z)))
assert sp.expand(div - (4 * z + x * z**2)) == 0

# (a) Divergence theorem over the solid cone (r <= z <= 2).
vol = sp.integrate(
    sp.integrate(
        sp.integrate((4 * z + r * sp.cos(th) * z**2) * r, (z, r, 2)), (r, 0, 2)
    ),
    (th, 0, 2 * sp.pi),
)
assert sp.simplify(vol - 16 * sp.pi) == 0

# (b) Cap z=2 (outward normal +k): F.k = 3y integrates to zero over the disc.
cap = sp.integrate(sp.integrate(3 * r * sp.sin(th) * r, (r, 0, 2)), (th, 0, 2 * sp.pi))
assert cap == 0

# (c) Direct integral over the lateral cone only: r(r,th)=(r cos, r sin, r),
#     outward normal element N = (r cos, r sin, -r) dr dth.
X, Y, Z = r * sp.cos(th), r * sp.sin(th), r
Fs = F.subs({x: X, y: Y, z: Z})
N = sp.Matrix([r * sp.cos(th), r * sp.sin(th), -r])
lateral = sp.integrate(sp.integrate(sp.simplify(Fs.dot(N)), (th, 0, 2 * sp.pi)), (r, 0, 2))
assert sp.simplify(lateral - 16 * sp.pi) == 0
assert sp.simplify(vol - cap - lateral) == 0
print("PASS EE-107-03-3")
