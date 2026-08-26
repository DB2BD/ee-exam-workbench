# -*- coding: utf-8 -*-
"""
math_verifier.py
================
Pi-Style Minimalist Mathematical & Engineering Verification Engine.
Provides deterministic symbolic and numerical verification for electrical engineering calculations:
- Phasor arithmetic & complex impedance
- Symmetrical components (0-1-2 <-> a-b-c)
- Per-unit conversion
- Matrix operations (Ybus, Zbus, inversion)
- Laplace transform & inverse Laplace
- Symbolic differential equations & algebraic solvers
"""

import sys
import json
import math
import cmath

try:
    import sympy as sp
    from sympy import symbols, Matrix, solve, dsolve, Function, Eq, laplace_transform, inverse_laplace_transform
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False


class MathVerifier:
    """Minimalist engineering math solver and verifier."""

    @staticmethod
    def complex_to_polar(z: complex) -> dict:
        """Convert a complex number to magnitude and angle (degrees)."""
        r, theta = cmath.polar(z)
        deg = math.degrees(theta)
        return {
            "real": z.real,
            "imag": z.imag,
            "magnitude": round(r, 6),
            "angle_deg": round(deg, 4),
            "polar_str": f"{r:.4f} ∠ {deg:.2f}°"
        }

    @staticmethod
    def polar_to_complex(r: float, deg: float) -> complex:
        """Convert magnitude and angle (degrees) to complex number."""
        theta = math.radians(deg)
        return cmath.rect(r, theta)

    @staticmethod
    def per_unit_conversion(z_old_pu: float, v_old: float, v_new: float, s_old: float, s_new: float) -> float:
        """
        Z_new_pu = Z_old_pu * (V_old / V_new)^2 * (S_new / S_old)
        """
        z_new = z_old_pu * ((v_old / v_new) ** 2) * (s_new / s_old)
        return round(z_new, 6)

    @staticmethod
    def symmetrical_components(ia: complex, ib: complex, ic: complex) -> dict:
        """
        Calculate symmetrical components (I0, I1, I2) from phase quantities (Ia, Ib, Ic).
        alpha = 1 ∠ 120° = -0.5 + j0.866025
        I0 = 1/3 * (Ia + Ib + Ic)
        I1 = 1/3 * (Ia + alpha*Ib + alpha^2*Ic)
        I2 = 1/3 * (Ia + alpha^2*Ib + alpha*Ic)
        """
        alpha = cmath.rect(1.0, math.radians(120))
        alpha2 = alpha * alpha

        i0 = (ia + ib + ic) / 3.0
        i1 = (ia + alpha * ib + alpha2 * ic) / 3.0
        i2 = (ia + alpha2 * ib + alpha * ic) / 3.0

        return {
            "zero_seq": MathVerifier.complex_to_polar(i0),
            "pos_seq": MathVerifier.complex_to_polar(i1),
            "neg_seq": MathVerifier.complex_to_polar(i2)
        }

    @staticmethod
    def solve_symbolic_equation(eq_str: str, var_str: str = "x") -> list:
        """Solve a symbolic equation using SymPy."""
        if not HAS_SYMPY:
            raise RuntimeError("SymPy is required for symbolic equation solving.")
        
        var = symbols(var_str)
        # Support eq_str as expression (=0) or LHS - RHS
        parsed_eq = sp.sympify(eq_str)
        solutions = solve(parsed_eq, var)
        return [str(sol) for sol in solutions]

    @staticmethod
    def invert_matrix_symbolic(matrix_nested_list: list) -> list:
        """Invert a numeric or symbolic square matrix."""
        if not HAS_SYMPY:
            raise RuntimeError("SymPy is required for matrix inversion.")
        M = Matrix(matrix_nested_list)
        M_inv = M.inv()
        return [[str(elem) for elem in row] for row in M_inv.tolist()]


def main():
    """CLI interface for Pi math verifier."""
    if len(sys.argv) < 2:
        print("Usage: python3 math_verifier.py '<command>' '<args_json>'")
        print("Commands: polar, rect, pu, sym_comp, solve_eq, invert_matrix")
        sys.exit(0)

    cmd = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    verifier = MathVerifier()
    
    if cmd == "polar":
        z = complex(args.get("real", 0), args.get("imag", 0))
        res = verifier.complex_to_polar(z)
        print(json.dumps(res, indent=2))
    elif cmd == "pu":
        res = verifier.per_unit_conversion(
            args["z_old"], args["v_old"], args["v_new"], args["s_old"], args["s_new"]
        )
        print(json.dumps({"z_new_pu": res}, indent=2))
    elif cmd == "sym_comp":
        ia = verifier.polar_to_complex(args["ia"]["r"], args["ia"]["deg"])
        ib = verifier.polar_to_complex(args["ib"]["r"], args["ib"]["deg"])
        ic = verifier.polar_to_complex(args["ic"]["r"], args["ic"]["deg"])
        res = verifier.symmetrical_components(ia, ib, ic)
        print(json.dumps(res, indent=2))
    elif cmd == "solve_eq":
        res = verifier.solve_symbolic_equation(args["equation"], args.get("var", "x"))
        print(json.dumps({"solutions": res}, indent=2))
    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))


if __name__ == "__main__":
    main()
