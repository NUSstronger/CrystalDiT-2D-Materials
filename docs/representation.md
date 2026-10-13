# Crystal Representation

DFCA encodes crystal structures as tensors suitable for neural network processing. This document describes the representation scheme.

## Design Principles

1. **Anisotropy awareness:** XY and Z coordinates are treated differently
2. **Physical interpretability:** Encoding based on periodic table structure
3. **Normalization:** All values scaled to [-1, 1] range for stable training
4. **Efficiency:** Fixed-size tensors for batch processing (max 20 atoms)

## Element Encoding

Each element is encoded by its position in the periodic table:

```
Atomic Number → (Period, Group) → Normalized (Period/7, Group/18)
```

| Element | Atomic Number | Period | Group | Encoded |
|---------|--------------|--------|-------|---------|
| H | 1 | 1 | 1 | (0.143, 0.056) |
| B | 5 | 2 | 13 | (0.286, 0.722) |
| C | 6 | 2 | 14 | (0.286, 0.778) |
| N | 7 | 2 | 15 | (0.286, 0.833) |
| ... | ... | ... | ... | ... |

**Rationale:** Period and group encode chemical behavior better than atomic number alone (same group → similar valence, same period → similar shell).

**Reference:** [`dfca/data/representation.py:ATOMIC_NUMBER_TO_POSITION`](dfca/data/representation.py)

## Lattice Representation

The 3×3 lattice matrix is normalized by MAX_LATTICE_LENGTH:

```python
MAX_LATTICE_LENGTH = 46.7425  # Å
normalized_lattice = lattice_matrix / MAX_LATTICE_LENGTH
```

This ensures all lattice values fall in approximately [-1, 1] for typical 2D slab structures.

### XY vs Z Treatment

The lattice matrix is decomposed into:
- **XY components:** a, b vectors and γ angle (in-plane)
- **Z components:** c vector (out-of-plane thickness)

In the CrystalDiT model:
- XY components: Processed by linear layer
- Z components: Processed by MLP (more complex mapping)

**Reference:** [`dfca/models/dit.py:CrystalEmbedder`](dfca/models/dit.py)

## Atom Representation

For each atom slot (up to max_atoms=20):

```python
atom_features = [
    period_normalized,      # [0, 1] (7 periods)
    group_normalized,        # [0, 1] (18 groups)
    x_fractional,           # [0, 1]
    y_fractional,           # [0, 1]
    z_fractional_centered    # [-1, 1] (centered at slab middle)
]
```

### Z-Centered Coordinates

For 2D slabs, z-coordinates are centered around the slab middle:

```python
z_centered = z_fractional - periodic_span_center
```

This accounts for variable vacuum thickness and ensures the slab is centered in the cell.

**Reference:** [`dfca/data/representation.py:periodic_span_center`](dfca/data/representation.py)

## Tensor Shapes

| Tensor | Shape | Description |
|--------|-------|-------------|
| `lattice_vectors` | (batch, 1, 3, 3) | Normalized 3×3 lattice matrix |
| `atom_features` | (batch, max_atoms, 5) | Element + fractional coordinates |
| `num_atoms` | (batch,) | Actual atom count per structure |

## Masking

Invalid atom slots (beyond `num_atoms`) are implicitly masked:
- Zero values in `atom_features` indicate empty slots
- Attention mechanism ignores padded positions

## Coordinate Conventions

| Coordinate | System | Reference |
|------------|--------|-----------|
| Lattice vectors | Cartesian | Lattice.matrix / MAX_LATTICE_LENGTH |
| Atom positions | Fractional | Structure.frac_coords |
| Z centering | Fractional | periodic_span_center |

**Reference:** [`dfca/data/representation.py:structure_to_representation`](dfca/data/representation.py)

## Usage

```python
from dfca.data.representation import structure_to_representation

# Convert pymatgen Structure to DFCA tensors
tensors = structure_to_representation(structure)
# Returns: {'lattice_vectors': Tensor, 'atom_features': Tensor, 'num_atoms': int}
```

---

*Last updated: 2026-10-01*
