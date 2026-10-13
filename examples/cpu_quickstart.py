#!/usr/bin/env python3
"""
DFCA CPU Quick Start — Crystal Representation and Model Interface Demo

This script demonstrates:
    1. Reading a crystal structure from CIF
    2. Converting it to DFCA representation format
    3. Constructing and inspecting the CrystalDiT model

This is an API demonstration only, NOT a scientific evaluation.
CPU forward pass is a software smoke test, not a quality assessment.

Requirements:
    - pymatgen (for CIF parsing)
    - torch
    - dfca package (in PYTHONPATH)

Run:
    PYTHONPATH=. python examples/cpu_quickstart.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import numpy as np

# =============================================================================
# PART 1: Read CIF and Parse Structure
# =============================================================================

def load_cif(cif_path):
    """
    Load a CIF file and parse it using pymatgen.

    Args:
        cif_path: Path to CIF file

    Returns:
        pymatgen Structure object
    """
    from pymatgen.core.structure import Structure

    with open(cif_path, 'r') as f:
        cif_string = f.read()

    structure = Structure.from_str(cif_string, fmt="cif")
    return structure


def print_structure_info(structure):
    """Print basic structure information."""
    print("\n" + "=" * 60)
    print("PART 1: Crystal Structure from CIF")
    print("=" * 60)

    print(f"\nFormula: {structure.composition.formula}")
    print(f"Number of atoms: {len(structure)}")
    print(f"Space group: {structure.get_space_group_info()}")

    print("\nLattice parameters:")
    lattice = structure.lattice
    print(f"  a = {lattice.a:.4f} Å")
    print(f"  b = {lattice.b:.4f} Å")
    print(f"  c = {lattice.c:.4f} Å")
    print(f"  α = {lattice.alpha:.2f}°")
    print(f"  β = {lattice.beta:.2f}°")
    print(f"  γ = {lattice.gamma:.2f}°")

    print("\nAtomic positions (fractional):")
    for site in structure:
        print(f"  {site.specie.symbol:2s}  ({site.frac_coords[0]:.4f}, {site.frac_coords[1]:.4f}, {site.frac_coords[2]:.4f})")


# =============================================================================
# PART 2: Convert to DFCA Representation
# =============================================================================

def structure_to_representation(structure, max_atoms=20):
    """
    Convert pymatgen Structure to DFCA representation tensors.

    This uses the exact same preprocessing as the training pipeline.

    Args:
        structure: pymatgen Structure
        max_atoms: Maximum number of atoms (padding size)

    Returns:
        dict with 'lattice_vectors' and 'atom_features' (both with batch dimension)
    """
    from dfca.data.representation import (
        MAX_LATTICE_LENGTH,
        ATOMIC_NUMBER_TO_POSITION,
        normalize_row,
        normalize_column,
        periodic_span_center,
    )

    # Get lattice vectors and normalize
    lattice_matrix = structure.lattice.matrix
    normalized_lattice = lattice_matrix / MAX_LATTICE_LENGTH

    # Get atom information
    atomic_numbers = []
    atom_coords = []

    for site in structure.sites:
        if len(atomic_numbers) >= max_atoms:
            break
        atomic_numbers.append(site.specie.Z)
        atom_coords.append([site.frac_coords[0], site.frac_coords[1], site.frac_coords[2]])

    # Center z coordinates for 2D materials
    if len(atom_coords) > 0:
        valid_z = [c[2] for c in atom_coords]
        z_center = periodic_span_center(valid_z)
        z_shift = 0.5 - z_center
        for c in atom_coords:
            c[2] = (c[2] + z_shift) % 1.0

    # Pad with invalid atoms if necessary
    while len(atomic_numbers) < max_atoms:
        atomic_numbers.append(0)  # Z=0 means invalid
        atom_coords.append([-1, -1, -1])

    # Convert atomic numbers to periodic table positions and normalize
    atom_features = []
    for z, coords in zip(atomic_numbers, atom_coords):
        if z > 0:  # Valid atom
            elem_row, elem_column = ATOMIC_NUMBER_TO_POSITION[z]
            norm_row = normalize_row(elem_row)
            norm_column = normalize_column(elem_column)
            atom_features.append([norm_row, norm_column, coords[0], coords[1], coords[2]])
        else:  # Invalid atom (padding)
            atom_features.append([-1, -1, -1, -1, -1])

    # Return with batch dimension [B, N, 5] and [B, 3, 3] to match model interface
    return {
        'lattice_vectors': torch.tensor(normalized_lattice, dtype=torch.float32).unsqueeze(0),
        'atom_features': torch.tensor(atom_features, dtype=torch.float32).unsqueeze(0),
        'num_atoms': len([z for z in atomic_numbers if z > 0]),
    }


def print_representation_info(rep):
    """Print representation tensor information."""
    print("\n" + "=" * 60)
    print("PART 2: DFCA Crystal Representation")
    print("=" * 60)

    lattice = rep['lattice_vectors']
    atoms = rep['atom_features']
    num_atoms = rep['num_atoms']

    print(f"\nLattice vectors tensor:")
    print(f"  Shape: {lattice.shape}  (batch, 3, 3)")
    print(f"  dtype: {lattice.dtype}")
    print(f"  Range: [{lattice.min():.4f}, {lattice.max():.4f}]")
    print(f"  All finite: {torch.all(torch.isfinite(lattice)).item()}")

    print(f"\nAtom features tensor:")
    print(f"  Shape: {atoms.shape}  (batch, max_atoms, 5)")
    print(f"  dtype: {atoms.dtype}")
    print(f"  All finite: {torch.all(torch.isfinite(atoms)).item()}")

    print(f"\n  Feature dimensions:")
    print(f"    [0] = normalized row (element period): range [{atoms[:,:,0].min():.4f}, {atoms[:,:,0].max():.4f}]")
    print(f"    [1] = normalized column (element group): range [{atoms[:,:,1].min():.4f}, {atoms[:,:,1].max():.4f}]")
    print(f"    [2] = fractional x: range [{atoms[:,:,2].min():.4f}, {atoms[:,:,2].max():.4f}]")
    print(f"    [3] = fractional y: range [{atoms[:,:,3].min():.4f}, {atoms[:,:,3].max():.4f}]")
    print(f"    [4] = fractional z (centered): range [{atoms[:,:,4].min():.4f}, {atoms[:,:,4].max():.4f}]")

    print(f"\n  Valid atoms: {num_atoms}")
    print(f"  Invalid (padded) atoms: {atoms.shape[1] - num_atoms}")

    # Show element encodings
    print(f"\n  Element encoding (first {num_atoms} atoms):")
    valid_mask = (atoms[0, :, 0] != -1)
    valid_atoms = atoms[0, valid_mask]
    for i, atom in enumerate(valid_atoms):
        z_row = (atom[0].item() + 1) / 2 * 7  # denormalize row
        z_col = (atom[1].item() + 1) / 2 * 18  # denormalize column
        print(f"    Atom {i+1}: row={atom[0]:+.4f}, col={atom[1]:+.4f}, pos=({atom[2]:.4f}, {atom[3]:.4f}, {atom[4]:.4f})")


# =============================================================================
# PART 3: Model Construction
# =============================================================================

def create_model(hidden_size=512, depth=18, num_heads=8, max_atoms=20):
    """
    Create a CrystalDiT model.

    Note: Default settings match production. A tiny model would NOT represent
    the actual DFCA architecture.
    """
    from dfca.models.dit import CrystalDiT

    model = CrystalDiT(
        max_atoms=max_atoms,
        hidden_size=hidden_size,
        depth=depth,
        num_heads=num_heads,
    )
    return model


def count_parameters(model):
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters())


def print_model_info(model):
    """Print model information."""
    print("\n" + "=" * 60)
    print("PART 3: CrystalDiT Model")
    print("=" * 60)

    print(f"\nModel type: CrystalDiT")
    print(f"  max_atoms: {model.max_atoms}")
    print(f"  hidden_size: {model.hidden_size}")
    print(f"  num_heads: {model.num_heads}")
    print(f"  depth: {len(model.blocks)}")
    print(f"  use_fusion: {model.use_fusion}")
    print(f"  cross_attn_mode: {model.cross_attn_mode}")

    total_params = count_parameters(model)
    print(f"\nTotal parameters: {total_params:,}")

    # Component breakdown
    embedder_params = sum(p.numel() for p in model.crystal_embedder.parameters())
    block_params = sum(p.numel() for p in model.blocks.parameters())
    final_params = sum(p.numel() for p in model.final_layer.parameters())

    print(f"\nParameter breakdown:")
    print(f"  CrystalEmbedder: {embedder_params:,}")
    print(f"  DiT Blocks ({len(model.blocks)}): {block_params:,}")
    print(f"  FinalLayer: {final_params:,}")


# =============================================================================
# PART 4: CPU Forward Smoke Test
# =============================================================================

def run_forward_smoke_test(model, lattice, atoms, device='cpu'):
    """
    Run a forward pass with the example data.

    This is a software smoke test only — it verifies the model can execute,
    not that it produces scientifically meaningful output.
    """
    print("\n" + "=" * 60)
    print("PART 4: CPU Forward Smoke Test")
    print("=" * 60)

    print("\nNOTE: CPU forward pass is a software/API smoke test only.")
    print("It does not evaluate generation quality or reproduce paper results.")
    print()

    model.eval()

    # Prepare input (already has batch dimension)
    lattice_batch = lattice.to(device)
    atoms_batch = atoms.to(device)
    timesteps = torch.tensor([500], device=device)  # Middle of diffusion schedule

    print(f"Input shapes:")
    print(f"  lattice_vectors: {lattice_batch.shape}")
    print(f"  atom_features: {atoms_batch.shape}")
    print(f"  timesteps: {timesteps.shape}")

    # Run forward pass
    import time
    start_time = time.time()

    with torch.no_grad():
        lattice_out, atom_out = model(lattice_batch, atoms_batch, timesteps)

    elapsed = time.time() - start_time

    print(f"\nOutput shapes:")
    print(f"  lattice_out: {lattice_out.shape}")
    print(f"  atom_out: {atom_out.shape}")

    print(f"\nForward pass time: {elapsed:.3f}s")
    print(f"Device: {device}")

    # Sanity checks
    # Note: lattice_batch is [B, 3, 3], atom_out is [B, N, F]
    assert lattice_out.shape == lattice_batch.shape, f"Lattice output shape mismatch: {lattice_out.shape} vs {lattice_batch.shape}"
    assert atom_out.shape == atoms_batch.shape, f"Atom output shape mismatch: {atom_out.shape} vs {atoms_batch.shape}"
    assert torch.all(torch.isfinite(lattice_out)), "Lattice output contains NaN/Inf"
    assert torch.all(torch.isfinite(atom_out)), "Atom output contains NaN/Inf"

    print("\n✓ Forward pass completed successfully")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("DFCA CPU Quick Start")
    print("Crystal Representation and Model Interface Demo")
    print("=" * 60)

    # Find example CIF
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cif_path = os.path.join(script_dir, "data", "example_2d_crystal.cif")

    if not os.path.exists(cif_path):
        print(f"\nERROR: Example CIF not found at: {cif_path}")
        print("Please ensure examples/data/example_2d_crystal.cif exists.")
        sys.exit(1)

    # Part 1: Load CIF
    print("\nLoading CIF file...")
    structure = load_cif(cif_path)
    print_structure_info(structure)

    # Part 2: Convert to representation
    print("\nConverting to DFCA representation...")
    rep = structure_to_representation(structure, max_atoms=20)
    print_representation_info(rep)

    # Part 3: Create model
    print("\nCreating CrystalDiT model...")
    model = create_model(hidden_size=512, depth=18, num_heads=8, max_atoms=20)
    print_model_info(model)

    # Part 4: Forward smoke test
    print("\n" + "-" * 60)
    print("CPU forward smoke test (may take a moment)...")
    print("-" * 60)

    try:
        run_forward_smoke_test(model, rep['lattice_vectors'], rep['atom_features'])
    except Exception as e:
        print(f"\nForward test skipped or failed: {e}")
        print("This is expected on CPU with large models.")

    print("\n" + "=" * 60)
    print("Quick Start Complete")
    print("=" * 60)
    print("\nFor GPU generation and training, see:")
    print("  - docs/training.md")
    print("  - docs/generation.md")
    print("  - docs/screening.md")


if __name__ == "__main__":
    main()
