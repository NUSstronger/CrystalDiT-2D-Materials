"""
Unit Tests: Representation Module - Self-Contained

Tests critical scientific constants and functions in dfca/data/representation.py.

Priority: HIGHEST - This is the foundation of all downstream behavior.

These tests verify the actual scientific values, not external comparisons.
"""

import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np
import torch


class TestRepresentationConstants(unittest.TestCase):
    """Test critical scientific constants have correct values."""

    def test_atomic_number_to_position_complete(self):
        """ATOMIC_NUMBER_TO_POSITION must contain all expected element mappings."""
        from dfca.data.representation import ATOMIC_NUMBER_TO_POSITION

        # Verify key elements are correctly mapped
        # H (Z=1): period 1, group 1
        self.assertEqual(ATOMIC_NUMBER_TO_POSITION[1], (1, 1), "H mapping incorrect")

        # C (Z=6): period 2, group 14
        self.assertEqual(ATOMIC_NUMBER_TO_POSITION[6], (2, 14), "C mapping incorrect")

        # O (Z=8): period 2, group 16
        self.assertEqual(ATOMIC_NUMBER_TO_POSITION[8], (2, 16), "O mapping incorrect")

        # N (Z=7): period 2, group 15
        self.assertEqual(ATOMIC_NUMBER_TO_POSITION[7], (2, 15), "N mapping incorrect")

        # Fe (Z=26): period 4, group 8
        self.assertEqual(ATOMIC_NUMBER_TO_POSITION[26], (4, 8), "Fe mapping incorrect")

        # Lanthanides merged to group 3
        # Ce (Z=58) and La (Z=57) should both map to (6, 3)
        self.assertEqual(ATOMIC_NUMBER_TO_POSITION[57], (6, 3), "La (lanthanide) mapping incorrect")
        self.assertEqual(ATOMIC_NUMBER_TO_POSITION[58], (6, 3), "Ce (lanthanide) mapping incorrect")

    def test_max_lattice_length(self):
        """MAX_LATTICE_LENGTH must be exactly 46.7425."""
        from dfca.data.representation import MAX_LATTICE_LENGTH

        self.assertEqual(MAX_LATTICE_LENGTH, 46.7425,
            "MAX_LATTICE_LENGTH must be 46.7425 for 18x18 lattice encoding")

    def test_atomic_number_to_mass_keys(self):
        """ATOMIC_NUMBER_TO_MASS must contain expected elements."""
        from dfca.data.representation import ATOMIC_NUMBER_TO_MASS

        # Verify key elements exist
        expected_elements = {1: 1.008, 6: 12.011, 8: 15.999, 26: 55.845}
        for z, expected_mass in expected_elements.items():
            self.assertIn(z, ATOMIC_NUMBER_TO_MASS, f"Element Z={z} missing from ATOMIC_NUMBER_TO_MASS")
            self.assertAlmostEqual(
                ATOMIC_NUMBER_TO_MASS[z], expected_mass, places=2,
                msg=f"Element Z={z} mass incorrect"
            )


class TestNormalizationFunctions(unittest.TestCase):
    """Test normalization/denormalization functions produce correct results."""

    def test_normalize_row_bijective(self):
        """normalize_row must be bijective with denormalize_row."""
        from dfca.data.representation import normalize_row, denormalize_row

        test_values = list(range(1, 8))  # Periods 1-7
        for v in test_values:
            normalized = normalize_row(v)
            denormalized = denormalize_row(normalized)
            self.assertEqual(
                v, denormalized,
                f"normalize_row/denormalize_row not bijective for period={v}"
            )

    def test_normalize_column_bijective(self):
        """normalize_column must be bijective with denormalize_column."""
        from dfca.data.representation import normalize_column, denormalize_column

        test_values = [1, 2, 13, 14, 15, 16, 17, 18]  # Group numbers
        for v in test_values:
            normalized = normalize_column(v)
            denormalized = denormalize_column(normalized)
            self.assertEqual(
                v, denormalized,
                f"normalize_column/denormalize_column not bijective for group={v}"
            )

    def test_normalize_row_range(self):
        """normalize_row must produce values in [-1, 1]."""
        from dfca.data.representation import normalize_row

        for period in range(1, 8):
            result = normalize_row(period)
            self.assertGreaterEqual(result, -1.0, f"normalize_row({period}) < -1")
            self.assertLessEqual(result, 1.0, f"normalize_row({period}) > 1")

    def test_normalize_column_range(self):
        """normalize_column must produce values in [-1, 1]."""
        from dfca.data.representation import normalize_column

        for group in range(1, 19):
            result = normalize_column(group)
            self.assertGreaterEqual(result, -1.0, f"normalize_column({group}) < -1")
            self.assertLessEqual(result, 1.0, f"normalize_column({group}) > 1")

    def test_invalid_encoding(self):
        """Z=0 (invalid) should map to neutral position (0, 0)."""
        from dfca.data.representation import (
            ATOMIC_NUMBER_TO_POSITION, normalize_row, normalize_column
        )

        period, group = ATOMIC_NUMBER_TO_POSITION[0]
        self.assertEqual(period, 0, "Invalid atom period should be 0")
        self.assertEqual(group, 0, "Invalid atom group should be 0")

        norm_row = normalize_row(period)
        norm_col = normalize_column(group)
        self.assertEqual(norm_row, -1, "Period 0 should normalize to -1")
        self.assertEqual(norm_col, -1, "Group 0 should normalize to -1")


class TestPeriodicSpanCenter(unittest.TestCase):
    """Test periodic_span_center function produces correct results."""

    def test_normal_case(self):
        """Normal fractional coordinates."""
        from dfca.data.representation import periodic_span_center

        values = [0.1, 0.2, 0.3]
        result = periodic_span_center(values)
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_wraps_around(self):
        """Coordinates that wrap around 0/1 boundary."""
        from dfca.data.representation import periodic_span_center

        values = [0.9, 0.95, 0.05, 0.1]
        result = periodic_span_center(values)
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_single_point(self):
        """Single coordinate should return itself."""
        from dfca.data.representation import periodic_span_center

        values = [0.5]
        result = periodic_span_center(values)
        self.assertEqual(result, 0.5)

    def test_empty(self):
        """Empty list should return 0.5 (center of [0,1])."""
        from dfca.data.representation import periodic_span_center

        values = []
        result = periodic_span_center(values)
        self.assertEqual(result, 0.5, "Empty list returns center of unit interval")


class TestValidElementLookups(unittest.TestCase):
    """Test VALID_ELEMENT_ROWCOL and VALID_ELEMENT_MASSES are correct."""

    def test_valid_element_rowcol_shape(self):
        """VALID_ELEMENT_ROWCOL must have expected shape."""
        from dfca.data.representation import VALID_ELEMENT_ROWCOL

        self.assertEqual(len(VALID_ELEMENT_ROWCOL.shape), 2, "VALID_ELEMENT_ROWCOL must be 2D")
        # Should be [E, 2] where E is number of valid elements (not atomic numbers)
        self.assertGreaterEqual(VALID_ELEMENT_ROWCOL.shape[0], 80, "Not enough valid elements")

    def test_valid_element_rowcol_values_range(self):
        """VALID_ELEMENT_ROWCOL values must be in normalized range [-1, 1]."""
        from dfca.data.representation import VALID_ELEMENT_ROWCOL

        min_val = VALID_ELEMENT_ROWCOL.min().item()
        max_val = VALID_ELEMENT_ROWCOL.max().item()
        self.assertGreaterEqual(min_val, -1.0, "VALID_ELEMENT_ROWCOL contains values < -1")
        self.assertLessEqual(max_val, 1.0, "VALID_ELEMENT_ROWCOL contains values > 1")

    def test_valid_element_masses_shape(self):
        """VALID_ELEMENT_MASSES must have correct shape."""
        from dfca.data.representation import VALID_ELEMENT_MASSES, VALID_ELEMENT_ROWCOL

        self.assertEqual(VALID_ELEMENT_MASSES.shape[0], VALID_ELEMENT_ROWCOL.shape[0],
            "VALID_ELEMENT_MASSES must have same first dimension as VALID_ELEMENT_ROWCOL")

    def test_valid_element_masses_positive(self):
        """VALID_ELEMENT_MASSES must all be positive."""
        from dfca.data.representation import VALID_ELEMENT_MASSES

        min_mass = VALID_ELEMENT_MASSES.min().item()
        self.assertGreater(min_mass, 0.0, "VALID_ELEMENT_MASSES contains non-positive values")


class TestElementMapping(unittest.TestCase):
    """Test element mapping functions produce correct encodings."""

    def test_hydrogen_encoding(self):
        """H (Z=1) should map to period=1, group=1."""
        from dfca.data.representation import ATOMIC_NUMBER_TO_POSITION

        period, group = ATOMIC_NUMBER_TO_POSITION[1]
        self.assertEqual(period, 1)
        self.assertEqual(group, 1)

    def test_carbon_encoding(self):
        """C (Z=6) should map to period=2, group=14."""
        from dfca.data.representation import ATOMIC_NUMBER_TO_POSITION

        period, group = ATOMIC_NUMBER_TO_POSITION[6]
        self.assertEqual(period, 2)
        self.assertEqual(group, 14)

    def test_lanthanide_merging(self):
        """Lanthanides should be merged to group 3."""
        from dfca.data.representation import ATOMIC_NUMBER_TO_POSITION

        # Ce (Z=58) and La (Z=57) should both map to (6, 3)
        ce = ATOMIC_NUMBER_TO_POSITION[58]
        la = ATOMIC_NUMBER_TO_POSITION[57]
        self.assertEqual(ce, (6, 3), "Ce (lanthanide) should map to period 6, group 3")
        self.assertEqual(la, (6, 3), "La (lanthanide) should map to period 6, group 3")


class TestDecodeAvgAtomicMass(unittest.TestCase):
    """Test decode_avg_atomic_mass function produces reasonable results."""

    def test_returns_positive_mass(self):
        """decode_avg_atomic_mass should return positive values."""
        from dfca.data.representation import decode_avg_atomic_mass

        # Any valid atom features should return positive mass
        atom_features = torch.tensor([[[0.0, 0.0, 0.5, 0.5, 0.5]]])
        result = decode_avg_atomic_mass(atom_features)
        self.assertGreater(result.item(), 0.0, "Atomic mass must be positive")

    def test_mass_in_reasonable_range(self):
        """decode_avg_atomic_mass should return mass in realistic range."""
        from dfca.data.representation import decode_avg_atomic_mass, VALID_ELEMENT_MASSES

        atom_features = torch.tensor([[[0.0, 0.0, 0.5, 0.5, 0.5]]])
        result = decode_avg_atomic_mass(atom_features)

        # Mass should be within the range of valid element masses
        min_mass = VALID_ELEMENT_MASSES.min().item()
        max_mass = VALID_ELEMENT_MASSES.max().item()
        self.assertGreaterEqual(result.item(), min_mass * 0.5,
            f"Mass {result.item()} too small (min valid: {min_mass})")
        self.assertLessEqual(result.item(), max_mass * 1.5,
            f"Mass {result.item()} too large (max valid: {max_mass})")


if __name__ == '__main__':
    unittest.main(verbosity=2)
