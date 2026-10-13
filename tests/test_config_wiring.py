"""
Configuration Wiring Tests.

Tests the configuration priority system:
    1. ScreeningConfig defaults (lowest)
    2. YAML config (overrides defaults)
    3. CLI arguments (highest priority)

Run with:
    python -m unittest tests.test_config_wiring -v
"""

import os
import sys
import tempfile
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dfca.screening.config import ScreeningConfig
from scripts.screen import apply_config_to_screening, load_yaml_config


def make_minimal_args():
    """Create a minimal args namespace with all required attributes."""
    import argparse
    args = argparse.Namespace()
    # Top-level
    args.input = None
    args.output = None
    args.train_csv = None
    args.device = None
    args.mace_model = None
    # Geometry
    args.vacuum_min = None
    args.thickness_max = None
    args.min_bond = None
    args.lattice_min = None
    args.lattice_max = None
    # Symmetry
    args.ltol = None
    args.stol = None
    args.angle_tol = None
    args.symprec = None
    # Relaxation
    args.relax_fmax = None
    args.relax_steps = None
    args.relax_steps_retry = None
    args.no_fix_z = False
    # Elastic
    args.elastic_delta = None
    # Phonon
    args.skip_phonon = False
    args.phonon_sc = None
    args.phonon_disp = None
    args.phonon_mesh = None
    args.imaginary_tol = None
    # Ehull
    args.ehull_thr = None
    args.no_ehull_gate = False
    args.mp_api_key = None
    # MD
    args.enable_md = False
    args.md_temp = None
    args.md_dt = None
    args.s7a_steps = None
    args.s7b_steps = None
    # Pipeline
    args.reject_p1 = False
    args.no_export_mag = False
    args.vasp_vacuum = None
    args.save_interval = None
    return args


class TestConfigWiring(unittest.TestCase):
    """Test configuration wiring with correct priority."""

    def test_defaults_no_yaml_no_cli(self):
        """Test 1: No YAML, no CLI -> ScreeningConfig defaults."""
        args = make_minimal_args()

        cfg = ScreeningConfig()
        yaml_config = {}

        result = apply_config_to_screening(cfg, yaml_config, args)

        # Check defaults are preserved
        self.assertEqual(result.vacuum_min_angstrom, 5.0)
        self.assertEqual(result.elastic_delta, 0.005)
        self.assertEqual(result.phonon_supercell, [3, 3, 1])
        self.assertEqual(result.phonon_displacement, 0.03)
        self.assertEqual(result.imaginary_freq_tol, -0.02)
        self.assertEqual(result.relax_steps, 400)
        self.assertEqual(result.ehull_threshold_ml, 0.2)
        self.assertEqual(result.md_temperature, 300.0)

    def test_yaml_vacuum_min(self):
        """Test 2: YAML vacuum_min=8 -> final cfg vacuum_min=8."""
        yaml_config = {
            'geometry': {
                'vacuum_min_angstrom': 8.0
            }
        }
        args = make_minimal_args()

        cfg = ScreeningConfig()
        result = apply_config_to_screening(cfg, yaml_config, args)

        self.assertEqual(result.vacuum_min_angstrom, 8.0)

    def test_yaml_relax_steps(self):
        """Test 3: YAML relax_steps=200 -> final cfg relax_steps=200."""
        yaml_config = {
            'relaxation': {
                'relax_steps': 200
            }
        }
        args = make_minimal_args()

        cfg = ScreeningConfig()
        result = apply_config_to_screening(cfg, yaml_config, args)

        self.assertEqual(result.relax_steps, 200)

    def test_yaml_elastic_delta(self):
        """Test 4: YAML elastic_delta=0.005 -> final cfg elastic_delta=0.005."""
        yaml_config = {
            'elastic': {
                'elastic_delta': 0.005
            }
        }
        args = make_minimal_args()

        cfg = ScreeningConfig()
        result = apply_config_to_screening(cfg, yaml_config, args)

        self.assertEqual(result.elastic_delta, 0.005)

    def test_yaml_phonon_settings(self):
        """Test 5: YAML phonon settings -> exact final values."""
        yaml_config = {
            'phonon': {
                'supercell': [3, 3, 1],
                'displacement': 0.03,
                'imaginary_freq_tol': -0.02
            }
        }
        args = make_minimal_args()

        cfg = ScreeningConfig()
        result = apply_config_to_screening(cfg, yaml_config, args)

        self.assertEqual(result.phonon_supercell, [3, 3, 1])
        self.assertEqual(result.phonon_displacement, 0.03)
        self.assertEqual(result.imaginary_freq_tol, -0.02)

    def test_yaml_value_plus_cli_override(self):
        """Test 6: YAML value + explicit CLI override -> CLI wins."""
        yaml_config = {
            'geometry': {
                'vacuum_min_angstrom': 8.0
            },
            'elastic': {
                'elastic_delta': 0.005
            }
        }
        args = make_minimal_args()
        args.vacuum_min = 10.0  # CLI override
        args.elastic_delta = 0.01  # CLI override

        cfg = ScreeningConfig()
        result = apply_config_to_screening(cfg, yaml_config, args)

        # CLI should win
        self.assertEqual(result.vacuum_min_angstrom, 10.0)
        self.assertEqual(result.elastic_delta, 0.01)

    def test_yaml_value_cli_not_supplied(self):
        """Test 7: YAML value + CLI not supplied -> YAML wins."""
        yaml_config = {
            'geometry': {
                'vacuum_min_angstrom': 8.0
            },
            'elastic': {
                'elastic_delta': 0.005
            }
        }
        args = make_minimal_args()
        # No vacuum_min or elastic_delta specified

        cfg = ScreeningConfig()
        result = apply_config_to_screening(cfg, yaml_config, args)

        # YAML should win (not overwritten by None)
        self.assertEqual(result.vacuum_min_angstrom, 8.0)
        self.assertEqual(result.elastic_delta, 0.005)

    def test_historical_cli_aliases(self):
        """Test 8: Historical CLI aliases map correctly."""
        args = make_minimal_args()

        # Historical aliases
        args.ehull_thr = 0.3
        args.elastic_delta = 0.01
        args.md_temp = 500.0
        args.md_dt = 2.0
        args.s7a_steps = 500
        args.s7b_steps = 2000
        args.no_export_mag = True

        cfg = ScreeningConfig()
        yaml_config = {}
        result = apply_config_to_screening(cfg, yaml_config, args)

        self.assertEqual(result.ehull_threshold_ml, 0.3)
        self.assertEqual(result.elastic_delta, 0.01)
        self.assertEqual(result.md_temperature, 500.0)
        self.assertEqual(result.md_dt_fs, 2.0)
        self.assertEqual(result.md_s7a_steps, 500)
        self.assertEqual(result.md_s7b_steps, 2000)
        self.assertEqual(result.export_mag_buckets, False)

    def test_config_file_is_loaded(self):
        """Test 9: --config is actually read."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
mace_model: medium
geometry:
  vacuum_min_angstrom: 12.0
  slab_thickness_max: 10.0
elastic:
  elastic_delta: 0.008
phonon:
  supercell: [4, 4, 1]
  displacement: 0.05
  imaginary_freq_tol: -0.05
""")
            temp_path = f.name

        try:
            yaml_config = load_yaml_config(temp_path)

            # Verify YAML was actually loaded
            self.assertEqual(yaml_config['mace_model'], 'medium')
            self.assertEqual(yaml_config['geometry']['vacuum_min_angstrom'], 12.0)
            self.assertEqual(yaml_config['elastic']['elastic_delta'], 0.008)
            self.assertEqual(yaml_config['phonon']['supercell'], [4, 4, 1])
        finally:
            os.unlink(temp_path)

    def test_mace_model_reaches_backend(self):
        """Test 10: mace_model=medium reaches backend model selector."""
        yaml_config = {
            'mace_model': 'medium'
        }
        args = make_minimal_args()

        cfg = ScreeningConfig()
        result = apply_config_to_screening(cfg, yaml_config, args)

        # Verify mace_model is set correctly
        self.assertEqual(result.mace_model, 'medium')

        # Verify backend would use it
        from dfca.screening.backend import MLBackend
        backend = MLBackend(device='cpu', model_size=result.mace_model)
        self.assertEqual(backend.model_size, 'medium')
        self.assertEqual(backend.name, 'mace-mp-medium')


class TestYAMLLoadConfig(unittest.TestCase):
    """Test YAML loading functionality."""

    def test_load_valid_yaml(self):
        """Test loading a valid YAML config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
device: cuda
mace_model: large
geometry:
  vacuum_min_angstrom: 15.0
""")
            temp_path = f.name

        try:
            config = load_yaml_config(temp_path)
            self.assertEqual(config['device'], 'cuda')
            self.assertEqual(config['mace_model'], 'large')
            self.assertEqual(config['geometry']['vacuum_min_angstrom'], 15.0)
        finally:
            os.unlink(temp_path)

    def test_load_missing_file(self):
        """Test that missing file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            load_yaml_config('/nonexistent/path/config.yaml')

    def test_load_empty_yaml(self):
        """Test loading YAML with no content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            config = load_yaml_config(temp_path)
            self.assertEqual(config, {})
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
