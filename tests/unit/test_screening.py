"""
Unit Tests: Screening Stage Parsers

Tests CPU-based parsing functions from screening stages.
No GPU or external DFT tools required.

Priority: MEDIUM - These are utility functions.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np


class TestThermodynamicsParser(unittest.TestCase):
    """Test thermodynamics parsing functions."""

    def test_compute_stability_label_high(self):
        """HIGH stability: negative formation, low e_hull."""
        from dfca.screening.stages.s_thermo import compute_stability_label

        result = compute_stability_label(e_form=-1.0, e_hull=0.1, threshold=0.2)
        self.assertEqual(result, "HIGH")

    def test_compute_stability_label_medium(self):
        """MEDIUM stability: negative formation, high e_hull."""
        from dfca.screening.stages.s_thermo import compute_stability_label

        result = compute_stability_label(e_form=-1.0, e_hull=0.3, threshold=0.2)
        self.assertEqual(result, "MEDIUM")

    def test_compute_stability_label_low(self):
        """LOW stability: positive formation energy."""
        from dfca.screening.stages.s_thermo import compute_stability_label

        result = compute_stability_label(e_form=0.5, e_hull=0.0, threshold=0.2)
        self.assertEqual(result, "LOW")

    def test_compute_stability_label_unknown(self):
        """UNKNOWN: e_hull is None."""
        from dfca.screening.stages.s_thermo import compute_stability_label

        result = compute_stability_label(e_form=-1.0, e_hull=None)
        self.assertEqual(result, "UNKNOWN")

    def test_compute_stability_label_custom_threshold(self):
        """Custom threshold value."""
        from dfca.screening.stages.s_thermo import compute_stability_label

        # e_hull=0.15 >= threshold=0.1 → MEDIUM
        result = compute_stability_label(e_form=-1.0, e_hull=0.15, threshold=0.1)
        self.assertEqual(result, "MEDIUM")

    def test_compute_stability_label_boundary(self):
        """Boundary case: e_hull exactly at threshold."""
        from dfca.screening.stages.s_thermo import compute_stability_label

        result = compute_stability_label(e_form=-1.0, e_hull=0.2, threshold=0.2)
        self.assertEqual(result, "MEDIUM")  # >= threshold = MEDIUM

    def test_diatomic_gases_set(self):
        """Diatomic gases constant is correct."""
        from dfca.screening.stages.s_thermo import _DIATOMIC_GASES

        expected = {"H", "N", "O", "F", "Cl", "Br", "I"}
        self.assertEqual(_DIATOMIC_GASES, expected)


class TestPhononParser(unittest.TestCase):
    """Test phonon stability parsing functions."""

    def test_adaptive_supercell_small(self):
        """Small structures get expanded supercell."""
        from dfca.screening.stages.s5_phonon import _adaptive_supercell

        # 1 atom structure
        result = _adaptive_supercell(1, [2, 2, 2], max_atoms=200)
        self.assertEqual(result[2], 1)  # z stays 1
        self.assertGreaterEqual(result[0], 5)
        self.assertGreaterEqual(result[1], 5)

    def test_adaptive_supercell_small_4atoms(self):
        """2-4 atom structures."""
        from dfca.screening.stages.s5_phonon import _adaptive_supercell

        result = _adaptive_supercell(3, [2, 2, 2], max_atoms=200)
        self.assertGreaterEqual(result[0], 4)
        self.assertGreaterEqual(result[1], 4)
        self.assertEqual(result[2], 1)

    def test_adaptive_supercell_medium(self):
        """5-8 atom structures."""
        from dfca.screening.stages.s5_phonon import _adaptive_supercell

        result = _adaptive_supercell(6, [2, 2, 2], max_atoms=200)
        self.assertGreaterEqual(result[0], 3)
        self.assertGreaterEqual(result[1], 3)
        self.assertEqual(result[2], 1)

    def test_adaptive_supercell_large(self):
        """Large structures keep base supercell."""
        from dfca.screening.stages.s5_phonon import _adaptive_supercell

        result = _adaptive_supercell(50, [2, 2, 2], max_atoms=200)
        # Should not expand much for large structures
        self.assertLessEqual(result[0], 3)
        self.assertLessEqual(result[1], 3)

    def test_adaptive_supercell_max_atoms(self):
        """Respects max_atoms limit."""
        from dfca.screening.stages.s5_phonon import _adaptive_supercell

        # 50 atoms with max 100 should shrink
        result = _adaptive_supercell(50, [3, 3, 3], max_atoms=100)
        self.assertLessEqual(50 * result[0] * result[1], 100)

    def test_adaptive_supercell_z_always_one(self):
        """z dimension always 1 for 2D structures."""
        from dfca.screening.stages.s5_phonon import _adaptive_supercell

        result = _adaptive_supercell(10, [5, 5, 5], max_atoms=200)
        self.assertEqual(result[2], 1)


class TestGeometryParser(unittest.TestCase):
    """Test geometry analysis functions."""

    def test_vacuum_calculation_basic(self):
        """Vacuum thickness calculation works correctly."""
        from dfca.screening.stages.s1_geometry import _vacuum_by_max_gap

        # Simple test case
        cart_z = np.array([1.0, 2.0, 3.0])
        c = 10.0  # Cell height
        vacuum, gap = _vacuum_by_max_gap(cart_z, c)

        # Vacuum should be positive and less than cell height
        self.assertIsInstance(vacuum, float)
        self.assertGreater(vacuum, 0)
        self.assertLess(vacuum, c)
        self.assertIsInstance(gap, float)

    def test_occupied_arc_basic(self):
        """Occupied arc calculation."""
        from dfca.screening.stages.s1_geometry import occupied_arc

        cart_z = np.array([0.1, 0.2, 0.3, 0.8, 0.9])
        c = 1.0
        arc = occupied_arc(cart_z, c)

        # Should return a positive fraction
        self.assertIsInstance(arc, float)
        self.assertGreater(arc, 0)
        self.assertLessEqual(arc, 1.0)


class TestSymmetryParser(unittest.TestCase):
    """Test symmetry analysis functions."""

    def test_hall_to_layer_group(self):
        """Hall number to layer group conversion."""
        from dfca.screening.stages.s2_symmetry import _hall_to_layer_group

        # Test known Hall number → layer group mappings
        result = _hall_to_layer_group(1)  # P1
        self.assertIsInstance(result, str)
        # Layer groups have format like "p1" or "p2_1" etc.
        self.assertGreater(len(result), 0)

    def test_check_symmetry_2d_signature(self):
        """check_symmetry_2d has correct signature."""
        import inspect
        from dfca.screening.stages.s2_symmetry import check_symmetry_2d

        sig = inspect.signature(check_symmetry_2d)
        params = list(sig.parameters.keys())

        # Should have struct and cfg parameters
        self.assertIn('struct', params)
        self.assertIn('cfg', params)


if __name__ == '__main__':
    unittest.main(verbosity=2)
