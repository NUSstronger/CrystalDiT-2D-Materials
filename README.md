# DFCA

An anisotropy-aware diffusion framework for two-dimensional crystal generation.

## Overview

DFCA is a research codebase for generating and screening 2D slab crystal structures using a crystal-specific diffusion transformer architecture. The framework implements the complete pipeline from training to first-principles validation.

**Key scientific focus:** Explicitly accounting for the anisotropic structural characteristics of two-dimensional crystals — where in-plane (XY) and out-of-plane (Z) degrees of freedom have distinct physical meanings — through separate representation and model treatment.

## Method

### Crystal Representation

The DFCA representation encodes crystal structures as tensors suitable for neural network processing:

- **Element encoding:** Atomic number → (period, group) in periodic table, normalized to [-1, 1]
- **Coordinate convention:** Fractional coordinates, with z-coordinates centered for 2D slabs
- **Lattice normalization:** All lattice vectors normalized by MAX_LATTICE_LENGTH = 46.7425 Å

Implementation: [`dfca/data/representation.py`](dfca/data/representation.py)

### Anisotropy-Aware Architecture

The CrystalDiT model uses separate embeddings for in-plane (XY) and out-of-plane (Z) components:

- **Lattice embedder:** Linear layer for XY, MLP for Z
- **Atom embedder:** Linear layer for XY features, MLP for Z features
- **Separate noise scales:** Different diffusion noise for Z coordinates (`z_noise_scale = 0.113001`) vs XY (`lattice_c_noise_scale = 0.340659`)

Implementation: [`dfca/models/dit.py`](dfca/models/dit.py)

### Diffusion Process

DFCA uses a DDPM-based diffusion process for crystal generation:

- **Noise schedule:** Linear beta schedule with 1000 timesteps
- **Objective:** Predict x₀ (starting state) from noisy input
- **Separate Z treatment:** Anisotropic noise scaling applied during forward diffusion

Implementation: [`dfca/diffusion/gaussian.py`](dfca/diffusion/gaussian.py)

### Physical Constraints

Training incorporates physics-based constraint losses with timestep-dependent weighting:

- Atom validity, lattice geometry, slab centering, density, vacuum thickness
- Decay boundaries at 30% and 70% of diffusion schedule

Implementation: [`dfca/training/constraints.py`](dfca/training/constraints.py)

## Repository Structure

```
dfca/
├── data/              # Crystal representation and preprocessing
├── models/            # CrystalDiT architecture
├── diffusion/         # Diffusion implementation (CrystalGaussianDiffusion)
├── training/          # Training workflow and constraints
├── generation/        # Crystal generation and decoding
├── screening/         # ML-based materials screening (S0-S7)
├── validation/        # GPAW first-principles validation
└── hpc/               # HPC utilities

diffusion/             # Third-party: OpenAI ADM/IDDPM/GLIDE base diffusion
├── gaussian_diffusion.py
├── model.py           # DiTBlock, TimestepEmbedder
└── ...

configs/               # YAML configuration files
├── train.yaml
├── generate.yaml
├── screening.yaml
└── dft_validation.yaml

scripts/
├── train.py           # Training entry point
└── generate.py        # Generation entry point

examples/
├── cpu_quickstart.py  # Minimal CPU demonstration
└── data/              # Example crystal structure

tests/                 # Unit and regression tests
docs/                  # Scientific documentation
```

## Quick Start

### CPU Demonstration

The CPU example demonstrates structure loading, DFCA representation, and model interface:

```bash
PYTHONPATH=. python examples/cpu_quickstart.py
```

This runs in ~0.1 seconds and does not execute full generation or training.

**Note:** CPU forward pass is a software/API smoke test only. It does not evaluate generation quality or reproduce paper results.

### Training

```bash
PYTHONPATH=. python scripts/train.py \
    --config configs/train.yaml \
    --data_dir ./Data \
    --output_dir ./output
```

Training requires GPU with CUDA. See [`docs/training.md`](docs/training.md) for detailed instructions.

### Generation

Generation requires a trained checkpoint (not included in repository):

```bash
PYTHONPATH=. python scripts/generate.py \
    --config configs/generate.yaml \
    --checkpoint /path/to/checkpoint \
    --output_dir ./candidates \
    --num_samples 100 \
    --device cuda
```

See [`docs/generation.md`](docs/generation.md) for detailed instructions.

## Screening Pipeline

Generated structures are screened through a two-phase pipeline:

### Phase 1: Fast Screening (CPU + ML)
```
Generated CIFs
      ↓
S0: Composition filter (element restrictions)
      ↓
S1: Geometry check (vacuum, thickness, bond distances)
      ↓
S2: Symmetry check (layer group)
      ↓
S3: Deduplication (structure similarity)
      ↓
S3.5: ML relaxation (MACE-MP-0)
      ↓
S-dim: Dimensionality check (2D connectivity)
      ↓
S3T: Thermodynamic stability (E_above_hull)
```

### Phase 2: Physics Validation (GPU/DFT)
```
S3T Pass
      ↓
S4: Elastic matrix (mechanical stability)
      ↓
S5: Phonon stability (phonopy + MACE forces)
      ↓
S7a: Short MD (thermal stability)
      ↓
S7b: Extended MD (long-term stability)
      ↓
S5': Final convex hull verification
```

Implementation: [`dfca/screening/pipeline.py`](dfca/screening/pipeline.py)

See [`docs/screening.md`](docs/screening.md) for detailed stage documentation.

## First-Principles Validation

Screened candidates are validated using GPAW DFT:

| Stage | Purpose | Method |
|-------|---------|--------|
| M1 | Structure relaxation | GPAW + PBE functional |
| M2 | Elastic constants | Finite difference |
| M3 | Phonon dispersion | Phonopy + GPAW |

**Note:** DFT validation requires the dedicated HPC environment (`environment/environment-dft.yml`).

See [`docs/dft_validation.md`](docs/dft_validation.md) for detailed documentation.

## Reproducibility

### Configuration

All parameters are configurable via YAML files in `configs/`:

```bash
# Training
configs/train.yaml

# Generation
configs/generate.yaml

# Screening
configs/screening.yaml

# DFT Validation
configs/dft_validation.yaml
```

### Randomness

Random seed can be set for reproducibility:

```bash
python scripts/train.py --config configs/train.yaml --seed 42
```

See [`docs/randomness_and_reproducibility.md`](docs/randomness_and_reproducibility.md) for detailed documentation.

### Reproducing the Paper

The complete paper workflow requires multiple stages with different environments:

#### Stage 1: Training
```bash
# Requires: GPU with CUDA, ML environment (environment-ml.yml)
PYTHONPATH=. python scripts/train.py \
    --config configs/train.yaml \
    --data_dir ./Data \
    --output_dir ./output
```

#### Stage 2: Generation
```bash
# Requires: Trained checkpoint from Stage 1
PYTHONPATH=. python scripts/generate.py \
    --config configs/generate.yaml \
    --checkpoint /path/to/checkpoint \
    --output_dir ./candidates \
    --num_samples 1000 \
    --device cuda
```

#### Stage 3: Screening
```bash
# Requires: Generated CIFs, GPU with MACE-MP-0
PYTHONPATH=. python scripts/screen.py \
    --config configs/screening.yaml \
    --input ./candidates \
    --output ./screened
```

#### Stage 4: DFT Validation
```bash
# Requires: HPC cluster with GPAW and MPI
PYTHONPATH=. python scripts/validate_dft.py \
    --config configs/dft_validation.yaml \
    --input ./screened \
    --output ./dft_results
```

**Note:** The CPU quickstart (`python examples/cpu_quickstart.py`) is a software smoke test only.
It does not reproduce paper generation quality or validate scientific results.

**Checkpoint and data availability:** Exact numerical reproduction requires the trained checkpoint
and Merged-2D dataset, which are not distributed in this source-code release.

### Testing

Tests are divided by environment requirements:

- **CPU tests:** Unit tests for representation and model structure
- **GPU tests:** Regression tests for training and generation
- **HPC tests:** DFT and MPI tests

```bash
# Run all CPU tests
PYTHONPATH=. python tests/unit/test_representation.py
PYTHONPATH=. python tests/unit/test_model.py
PYTHONPATH=. python tests/regression/test_diffusion.py
```

See [`docs/testing.md`](docs/testing.md) for full test matrix.

## Data

The DFCA training dataset is the **Merged-2D** dataset, constructed from:

- **C2DB** (Computational 2D Materials Database): https://cmr.fysik.dtu.dk/c2db/c2db.html
- **2DMatPedia**: http://www.2dmaterials.org/

**Final filtered dataset: 17,654 structures**

**Data redistribution:** Raw C2DB and 2DMatPedia data are **NOT redistributed** in this
source-code release pending verification of redistribution terms. See [`docs/data.md`](docs/data.md)
for detailed provenance information, licensing status, and instructions for obtaining
and preprocessing the data from the original sources.

To reproduce DFCA training:
1. Visit https://cmr.fysik.dtu.dk/c2db/c2db.html and download C2DB (requires registration)
2. Visit http://www.2dmaterials.org/ and download 2DMatPedia
3. Follow preprocessing instructions in [`dfca/data/preprocessing.py`](dfca/data/preprocessing.py)
4. Combine and filter structures (see [`docs/data.md`](docs/data.md) for the 17,654-structure Merged-2D protocol)
5. Generate train/val/test splits

## Pretrained Models

Pretrained DFCA checkpoints will be released with the manuscript.

## Citation

Citation information will be updated upon preprint/publication.

## License

Licensing terms are being finalized prior to public release. See [`LICENSE`](LICENSE) file for current status.

## Third-Party Code

DFCA builds upon several third-party implementations:

- **GaussianDiffusion base class:** Modified from OpenAI's ADM/IDDPM/GLIDE repositories
  - ADM: https://github.com/openai/guided-diffusion
  - IDDPM: https://github.com/openai/improved-diffusion
  - GLIDE: https://github.com/openai/glide-text2im

- **DiT architecture:** Based on standard transformer patterns for diffusion models

See [`THIRD_PARTY.md`](THIRD_PARTY.md) for detailed acknowledgments.

## Acknowledgments

- C2DB (Computational 2D Materials Database)
- OpenAI for diffusion model infrastructure
- MACE potential authors
- GPAW developers
- pymatgen developers
