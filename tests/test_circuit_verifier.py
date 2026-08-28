# -*- coding: utf-8 -*-
"""Tests for the deterministic Pi-harness modified nodal analysis engine."""

import unittest

from scripts.tools.circuit_verifier import CircuitVerifier, CircuitSingularError


class TestCircuitVerifier(unittest.TestCase):

    def test_resistive_divider_with_voltage_source(self):
        result = CircuitVerifier.solve_mna(
            node_count=2,
            passive_elements=[
                {"type": "R", "n1": 2, "n2": 1, "value": 1000.0},
                {"type": "R", "n1": 1, "n2": 0, "value": 2000.0},
            ],
            voltage_sources=[{"n_plus": 2, "n_minus": 0, "voltage": 12.0}],
        )

        self.assertAlmostEqual(result.node_voltages[1].real, 8.0, places=8)
        self.assertAlmostEqual(result.node_voltages[2].real, 12.0, places=8)
        self.assertLess(result.max_kcl_residual, 1e-9)
        self.assertTrue(result.constraints_ok)

    def test_controlled_voltage_source(self):
        result = CircuitVerifier.solve_mna(
            node_count=2,
            voltage_sources=[{"n_plus": 1, "n_minus": 0, "voltage": 2.0}],
            controlled_voltage_sources=[{
                "n_plus": 2,
                "n_minus": 0,
                "control_plus": 1,
                "control_minus": 0,
                "gain": 5.0,
            }],
        )

        self.assertAlmostEqual(result.node_voltages[1].real, 2.0, places=8)
        self.assertAlmostEqual(result.node_voltages[2].real, 10.0, places=8)
        self.assertLess(result.max_kcl_residual, 1e-9)
        self.assertTrue(result.constraints_ok)

    def test_complex_admittance_ac_network(self):
        result = CircuitVerifier.solve_mna(
            node_count=1,
            passive_elements=[
                {"type": "R", "n1": 1, "n2": 0, "value": 10.0},
                {"type": "C", "n1": 1, "n2": 0, "value": 1e-3},
            ],
            voltage_sources=[{"n_plus": 1, "n_minus": 0, "voltage": 1.0}],
            frequency_hz=1000.0,
        )

        self.assertAlmostEqual(result.node_voltages[1].real, 1.0, places=8)
        self.assertAlmostEqual(result.node_voltages[1].imag, 0.0, places=8)
        self.assertLess(result.max_kcl_residual, 1e-9)

    def test_singular_network_is_rejected(self):
        with self.assertRaises(CircuitSingularError):
            CircuitVerifier.solve_mna(
                node_count=1,
                passive_elements=[{"type": "R", "n1": 1, "n2": 0, "value": 0.0}],
            )


if __name__ == "__main__":
    unittest.main()
