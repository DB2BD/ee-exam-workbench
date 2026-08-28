# -*- coding: utf-8 -*-
"""Deterministic modified nodal analysis for Pi-harness circuit verification.

This module is intentionally small and dependency-free.  It is a verifier, not
an LLM solver: the caller supplies a circuit model and receives node voltages,
branch currents, and residual checks that can reject an inconsistent solution.
Supported elements are R, L, C, explicit admittances, independent current and
voltage sources, and voltage-controlled voltage sources (VCVS).
"""

from dataclasses import dataclass
import json
import math
import sys
from typing import Dict, Iterable, List, Optional, Sequence


class CircuitSingularError(ValueError):
    """Raised when the supplied circuit has no unique MNA solution."""


@dataclass
class CircuitResult:
    node_voltages: Dict[int, complex]
    branch_currents: List[complex]
    max_kcl_residual: float
    max_constraint_residual: float
    constraints_ok: bool
    matrix_size: int


def _complex(value) -> complex:
    if isinstance(value, complex):
        return value
    if isinstance(value, (int, float)):
        return complex(value, 0.0)
    if isinstance(value, str):
        return complex(value.replace("i", "j"))
    raise TypeError("circuit values must be numeric or complex")


def _node_index(node: int, node_count: int) -> Optional[int]:
    if not isinstance(node, int) or isinstance(node, bool):
        raise TypeError("node numbers must be integers")
    if node == 0:
        return None
    if node < 1 or node > node_count:
        raise ValueError("node number is outside the declared node_count")
    return node - 1


def _stamp_admittance(matrix: List[List[complex]], n1: int, n2: int, value: complex) -> None:
    """Stamp a two-terminal admittance into the conductance matrix."""
    if n1 is not None:
        matrix[n1][n1] += value
    if n2 is not None:
        matrix[n2][n2] += value
    if n1 is not None and n2 is not None:
        matrix[n1][n2] -= value
        matrix[n2][n1] -= value


def _element_admittance(element: dict, frequency_hz: Optional[float]) -> complex:
    kind = str(element.get("type", "")).upper()
    value = _complex(element.get("value"))
    if kind == "Y":
        return value
    if kind == "R":
        if abs(value) <= 1e-15:
            raise CircuitSingularError("zero-ohm resistor requires topology reduction")
        return 1.0 / value

    frequency = float(frequency_hz or 0.0)
    if frequency <= 0.0:
        if kind == "C":
            return 0.0j  # capacitor is open at DC
        raise CircuitSingularError("an ideal inductor at DC requires topology reduction")
    omega = 2.0 * math.pi * frequency
    if kind == "C":
        return 1j * omega * value
    if kind == "L":
        if abs(value) <= 1e-30:
            raise CircuitSingularError("zero-inductance element is invalid")
        return 1.0 / (1j * omega * value)
    raise ValueError("unsupported passive element type: %s" % kind)


def _gaussian_solve(matrix: Sequence[Sequence[complex]], rhs: Sequence[complex]) -> List[complex]:
    """Solve a complex square system with partial pivoting."""
    size = len(rhs)
    work = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    tolerance = 1e-12

    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(work[row][col]))
        if abs(work[pivot][col]) <= tolerance:
            raise CircuitSingularError("singular or under-constrained circuit matrix")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]

        divisor = work[col][col]
        work[col] = [entry / divisor for entry in work[col]]
        for row in range(size):
            if row == col:
                continue
            factor = work[row][col]
            if abs(factor) <= tolerance:
                continue
            work[row] = [
                work[row][i] - factor * work[col][i]
                for i in range(size + 1)
            ]
    return [work[i][size] for i in range(size)]


class CircuitVerifier:
    """Solve and audit linear electrical networks using modified nodal analysis."""

    @staticmethod
    def solve_mna(
        node_count: int,
        passive_elements: Optional[Iterable[dict]] = None,
        current_sources: Optional[Iterable[dict]] = None,
        voltage_sources: Optional[Iterable[dict]] = None,
        controlled_voltage_sources: Optional[Iterable[dict]] = None,
        frequency_hz: Optional[float] = None,
        residual_tolerance: float = 1e-9,
    ) -> CircuitResult:
        if not isinstance(node_count, int) or node_count < 1:
            raise ValueError("node_count must be a positive integer")

        passive = list(passive_elements or [])
        currents = list(current_sources or [])
        voltages = list(voltage_sources or [])
        controlled = list(controlled_voltage_sources or [])
        branch_count = len(voltages) + len(controlled)
        size = node_count + branch_count
        matrix = [[0.0j for _ in range(size)] for _ in range(size)]
        rhs = [0.0j for _ in range(size)]

        for element in passive:
            n1 = _node_index(element["n1"], node_count)
            n2 = _node_index(element["n2"], node_count)
            _stamp_admittance(matrix, n1, n2, _element_admittance(element, frequency_hz))

        for source in currents:
            n_plus = _node_index(source["n_plus"], node_count)
            n_minus = _node_index(source["n_minus"], node_count)
            current = _complex(source["current"])
            # MNA node equations use injected current on the right-hand side.
            if n_plus is not None:
                rhs[n_plus] -= current
            if n_minus is not None:
                rhs[n_minus] += current

        def stamp_voltage_branch(branch_index: int, n_plus: int, n_minus: int) -> None:
            if n_plus is not None:
                matrix[n_plus][branch_index] += 1.0
                matrix[branch_index][n_plus] += 1.0
            if n_minus is not None:
                matrix[n_minus][branch_index] -= 1.0
                matrix[branch_index][n_minus] -= 1.0

        for idx, source in enumerate(voltages):
            row = node_count + idx
            n_plus = _node_index(source["n_plus"], node_count)
            n_minus = _node_index(source["n_minus"], node_count)
            stamp_voltage_branch(row, n_plus, n_minus)
            rhs[row] = _complex(source["voltage"])

        for idx, source in enumerate(controlled):
            row = node_count + len(voltages) + idx
            out_plus = _node_index(source["n_plus"], node_count)
            out_minus = _node_index(source["n_minus"], node_count)
            ctrl_plus = _node_index(source["control_plus"], node_count)
            ctrl_minus = _node_index(source["control_minus"], node_count)
            gain = _complex(source["gain"])
            stamp_voltage_branch(row, out_plus, out_minus)
            # V(out+) - V(out-) = gain * (V(ctrl+) - V(ctrl-)).
            if ctrl_plus is not None:
                matrix[row][ctrl_plus] -= gain
            if ctrl_minus is not None:
                matrix[row][ctrl_minus] += gain

        solution = _gaussian_solve(matrix, rhs)
        node_voltages = {node: solution[node - 1] for node in range(1, node_count + 1)}
        branch_currents = solution[node_count:]

        node_residuals = []
        for row in range(node_count):
            node_residuals.append(sum(matrix[row][col] * solution[col] for col in range(size)) - rhs[row])
        constraint_residuals = []
        for row in range(node_count, size):
            constraint_residuals.append(sum(matrix[row][col] * solution[col] for col in range(size)) - rhs[row])

        max_kcl = max((abs(value) for value in node_residuals), default=0.0)
        max_constraint = max((abs(value) for value in constraint_residuals), default=0.0)
        constraints_ok = max(max_kcl, max_constraint) <= residual_tolerance
        return CircuitResult(
            node_voltages=node_voltages,
            branch_currents=branch_currents,
            max_kcl_residual=max_kcl,
            max_constraint_residual=max_constraint,
            constraints_ok=constraints_ok,
            matrix_size=size,
        )


def _json_value(value: complex):
    if abs(value.imag) <= 1e-12:
        return round(value.real, 12)
    return {"real": round(value.real, 12), "imag": round(value.imag, 12)}


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] != "solve":
        print("Usage: python3 circuit_verifier.py solve '<circuit_json>'")
        raise SystemExit(2)
    result = CircuitVerifier.solve_mna(**json.loads(sys.argv[2]))
    print(json.dumps({
        "node_voltages": {str(k): _json_value(v) for k, v in result.node_voltages.items()},
        "branch_currents": [_json_value(v) for v in result.branch_currents],
        "max_kcl_residual": result.max_kcl_residual,
        "max_constraint_residual": result.max_constraint_residual,
        "constraints_ok": result.constraints_ok,
        "matrix_size": result.matrix_size,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
