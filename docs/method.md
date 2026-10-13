# Method

DFCA (Diffusion Framework for Crystal Anisotropy) is a research framework for generating and screening two-dimensional crystal structures using an anisotropy-aware diffusion model.

## Core Innovation: Anisotropic Treatment of 2D Crystals

Unlike bulk 3D crystals where all three lattice directions have similar physical meaning, 2D slab crystals have fundamentally different in-plane (XY) and out-of-plane (Z) degrees of freedom:

- **In-plane (XY):** Chemical bonding, periodic structure, atomic arrangement
- **Out-of-plane (Z):** Vacuum padding, slab thickness, layer stacking

DFCA explicitly models this anisotropy through:

1. **Separate representation:** Different encoding for XY vs Z coordinates
2. **Separate model treatment:** Different neural network architectures for XY vs Z
3. **Separate noise scaling:** Different diffusion noise levels for Z vs XY
4. **Separate loss weighting:** Different loss weights for Z vs XY features

## Architecture Overview

```
Input Crystal Structure
         ↓
┌─────────────────────────────────────┐
│  Crystal Representation             │
│  - Element encoding (period, group) │
│  - Lattice normalization (XY/Z)     │
│  - Fractional coordinates (Z-center)│
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  CrystalDiT (Diffusion Transformer) │
│  - Lattice embedder (XY linear, Z MLP)     │
│  - Atom embedder (XY linear, Z MLP)        │
│  - Transformer blocks               │
│  - Anisotropic attention            │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  CrystalGaussianDiffusion           │
│  - DDPM with 1000 timesteps         │
│  - Separate Z noise scale           │
│  - Physical constraint losses       │
└─────────────────────────────────────┘
         ↓
Generated Crystal Structures
```

## Training Pipeline

1. **Data loading:** Crystal structures from Merged-2D dataset (C2DB + 2DMatPedia, 17,654 structures)
2. **Representation:** Convert to DFCA tensor format
3. **Forward diffusion:** Apply anisotropic noise at timestep t
4. **Model prediction:** CrystalDiT predicts x₀ from noisy input
5. **Loss computation:** Combined MSE + physical constraints
6. **Optimization:** AdamW with timestep-dependent weighting

See [`docs/training.md`](training.md) for detailed training documentation and [`docs/data.md`](data.md) for dataset provenance.

## Generation Pipeline

1. **Sampling:** Start from random noise
2. **Denoising:** Iteratively apply model prediction (1000 steps)
3. **Decoding:** Convert tensors back to crystal structures
4. **CIF output:** Export valid structures for screening

See [`docs/generation.md`](generation.md) for detailed generation documentation.

## Screening Pipeline

Generated structures pass through multi-stage screening:

1. **S0:** Composition filter (element restrictions)
2. **S1:** Geometry check (vacuum, thickness, bonds)
3. **S2:** Symmetry check (layer group)
4. **S3:** Deduplication (structure similarity)
5. **S3.5:** ML relaxation (MACE-MP-0)
6. **S5:** Phonon stability (phonopy + MACE)
7. **Thermodynamic:** E_above_hull calculation

See [`docs/screening.md`](screening.md) for detailed screening documentation.

## DFT Validation

Screened candidates undergo first-principles validation:

1. **M1:** Structure relaxation (GPAW + PBE)
2. **M2:** Elastic constants (finite difference)
3. **M3:** Phonon dispersion (phonopy + GPAW)

See [`docs/dft_validation.md`](dft_validation.md) for detailed DFT documentation.

---

*For implementation details, see source code:*
- [`dfca/data/representation.py`](dfca/data/representation.py)
- [`dfca/models/dit.py`](dfca/models/dit.py)
- [`dfca/diffusion/gaussian.py`](dfca/diffusion/gaussian.py)
- [`dfca/training/constraints.py`](dfca/training/constraints.py)
