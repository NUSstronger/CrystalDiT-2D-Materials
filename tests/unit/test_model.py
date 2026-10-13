"""
Unit Tests: Model Architecture

Tests dfca/models/dit.py to ensure structural correctness.

Priority: HIGH - Model checkpoint compatibility depends on this.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import torch
import numpy as np


class TestModelStructure(unittest.TestCase):
    """Test model structure is correct."""

    def test_crystal_embedder_structure(self):
        """CrystalEmbedder must have same architecture as original."""
        from dfca.models.dit import CrystalEmbedder

        # Create embedder
        embedder = CrystalEmbedder(hidden_size=128, max_atoms=20)

        # Check key components exist
        self.assertTrue(hasattr(embedder, 'lattice_embedder_xy'))
        self.assertTrue(hasattr(embedder, 'lattice_embedder_z'))
        self.assertTrue(hasattr(embedder, 'atom_embedder_xy'))
        self.assertTrue(hasattr(embedder, 'atom_embedder_z'))
        self.assertTrue(hasattr(embedder, 'lattice_type_embedding'))
        self.assertTrue(hasattr(embedder, 'atom_type_embedding'))
        self.assertTrue(hasattr(embedder, 'lattice_pos_embed'))

    def test_crystal_embedder_input_shapes(self):
        """CrystalEmbedder must handle correct input shapes."""
        from dfca.models.dit import CrystalEmbedder

        embedder = CrystalEmbedder(hidden_size=128, max_atoms=20)

        batch_size = 2
        lattice_vectors = torch.randn(batch_size, 3, 3)  # [B, 3, 3]
        atom_features = torch.randn(batch_size, 20, 5)   # [B, N, 5]

        lattice_emb, atom_emb = embedder(lattice_vectors, atom_features)

        self.assertEqual(lattice_emb.shape, (batch_size, 3, 128))
        self.assertEqual(atom_emb.shape, (batch_size, 20, 128))

    def test_final_layer_structure(self):
        """FinalLayer must have same architecture as original."""
        from dfca.models.dit import FinalLayer

        layer = FinalLayer(hidden_size=128)

        # Check key components
        self.assertTrue(hasattr(layer, 'norm_final_lattice'))
        self.assertTrue(hasattr(layer, 'norm_final_atom'))
        self.assertTrue(hasattr(layer, 'lattice_linear'))
        self.assertTrue(hasattr(layer, 'atom_linear'))
        self.assertTrue(hasattr(layer, 'adaLN_modulation'))

        # Check output dimensions
        atom_feat = torch.randn(2, 20, 128)
        lattice_feat = torch.randn(2, 3, 128)
        cond = torch.randn(2, 128)

        lattice_out, atom_out = layer(atom_feat, lattice_feat, cond)

        self.assertEqual(lattice_out.shape, (2, 3, 3))
        self.assertEqual(atom_out.shape, (2, 20, 5))

    def test_crystal_dit_structure(self):
        """CrystalDiT must have expected structure."""
        from dfca.models.dit import CrystalDiT, count_parameters

        model = CrystalDiT(
            max_atoms=20,
            hidden_size=128,
            depth=2,  # Small for testing
            num_heads=4
        )

        # Check main components
        self.assertTrue(hasattr(model, 'crystal_embedder'))
        self.assertTrue(hasattr(model, 't_embedder'))
        self.assertTrue(hasattr(model, 'blocks'))
        self.assertTrue(hasattr(model, 'final_layer'))

        # Check config preserved
        self.assertEqual(model.max_atoms, 20)
        self.assertEqual(model.hidden_size, 128)
        self.assertEqual(model.num_heads, 4)

        # Check parameter count is reasonable
        param_count = count_parameters(model)
        self.assertGreater(param_count, 1000)  # At least some parameters

    def test_crystal_dit_forward_shapes(self):
        """CrystalDiT forward pass must produce correct shapes."""
        from dfca.models.dit import CrystalDiT

        model = CrystalDiT(
            max_atoms=20,
            hidden_size=128,
            depth=2,
            num_heads=4
        )
        model.eval()  # Set to eval mode for deterministic behavior

        batch_size = 2
        lattice_vectors = torch.randn(batch_size, 3, 3)
        atom_features = torch.randn(batch_size, 20, 5)
        t = torch.randint(0, 1000, (batch_size,))

        lattice_out, atom_out = model(lattice_vectors, atom_features, t)

        self.assertEqual(lattice_out.shape, (batch_size, 3, 3))
        self.assertEqual(atom_out.shape, (batch_size, 20, 5))

    def test_crystal_dit_padding_mask(self):
        """CrystalDiT must handle padding mask correctly."""
        from dfca.models.dit import CrystalDiT

        model = CrystalDiT(max_atoms=20, hidden_size=128, depth=2, num_heads=4)
        model.eval()

        batch_size = 2
        lattice_vectors = torch.randn(batch_size, 3, 3)
        atom_features = torch.randn(batch_size, 20, 5)
        t = torch.randint(0, 1000, (batch_size,))

        # Create padding mask (True = padded)
        padding_mask = torch.tensor([[False, False, True, True] + [True] * 16,
                                     [False] * 10 + [True] * 10])

        lattice_out, atom_out = model(
            lattice_vectors, atom_features, t, padding_mask=padding_mask
        )

        self.assertEqual(lattice_out.shape, (batch_size, 3, 3))
        self.assertEqual(atom_out.shape, (batch_size, 20, 5))


class TestModelStateDict(unittest.TestCase):
    """Test model state_dict format is preserved."""

    def test_state_dict_keys(self):
        """State dict keys must match expected pattern."""
        from dfca.models.dit import CrystalDiT

        model = CrystalDiT(max_atoms=20, hidden_size=128, depth=2, num_heads=4)
        state_dict = model.state_dict()

        # Check essential keys exist
        self.assertIn('crystal_embedder.lattice_embedder_xy.weight', state_dict)
        self.assertIn('crystal_embedder.atom_embedder_xy.weight', state_dict)
        # t_embedder may be .linear or .mlp depending on version
        t_embedder_keys = [k for k in state_dict.keys() if k.startswith('t_embedder')]
        self.assertGreater(len(t_embedder_keys), 0, "t_embedder keys not found")
        self.assertIn('final_layer.lattice_linear.weight', state_dict)
        self.assertIn('final_layer.atom_linear.weight', state_dict)

    def test_state_dict_shapes(self):
        """State dict shapes must be consistent."""
        from dfca.models.dit import CrystalDiT

        model = CrystalDiT(max_atoms=20, hidden_size=128, depth=2, num_heads=4)
        state_dict = model.state_dict()

        # Check critical shapes
        self.assertEqual(state_dict['crystal_embedder.lattice_embedder_xy.weight'].shape,
                        (64, 2))  # hidden_size//2 x 2
        self.assertEqual(state_dict['crystal_embedder.atom_embedder_xy.weight'].shape,
                        (64, 4))  # hidden_size//2 x 4
        self.assertEqual(state_dict['final_layer.lattice_linear.weight'].shape,
                        (3, 128))  # 3 x hidden_size
        self.assertEqual(state_dict['final_layer.atom_linear.weight'].shape,
                        (5, 128))  # 5 x hidden_size


class TestTimestepEmbedder(unittest.TestCase):
    """Test timestep embedder is preserved."""

    def test_timestep_embedder_output_shape(self):
        """TimestepEmbedder must produce correct output shape."""
        from diffusion.model import TimestepEmbedder

        embedder = TimestepEmbedder(hidden_size=128)

        # Single timestep
        t = torch.tensor([100])
        out = embedder(t)
        self.assertEqual(out.shape, (1, 128))

        # Batch of timesteps
        t = torch.randint(0, 1000, (4,))
        out = embedder(t)
        self.assertEqual(out.shape, (4, 128))


class TestModelParameterInitialization(unittest.TestCase):
    """Test model parameter initialization is preserved."""

    def test_embedder_initialization(self):
        """Embedder must initialize weights correctly."""
        from dfca.models.dit import CrystalEmbedder

        # Create two instances with same seed
        torch.manual_seed(42)
        embedder1 = CrystalEmbedder(hidden_size=64, max_atoms=10)

        torch.manual_seed(42)
        embedder2 = CrystalEmbedder(hidden_size=64, max_atoms=10)

        # Same seed should produce same weights
        sd1 = embedder1.state_dict()
        sd2 = embedder2.state_dict()

        for key in sd1:
            self.assertTrue(
                torch.equal(sd1[key], sd2[key]),
                f"Weight mismatch for {key}"
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
