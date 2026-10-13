# DFCA: Diffusion Framework for Crystal Anisotropy

**An anisotropy-aware diffusion framework for two-dimensional crystal generation and screening.**

*Engineering Applications of Artificial Intelligence (EAAI)*

---

## Table of Contents

1. [Overview](#overview)
2. [Key Contributions](#key-contributions)
3. [Architecture](#architecture)
4. [Physics-Informed Training](#physics-informed-training)
5. [Benchmark Results](#benchmark-results)
6. [Engineering Screening and Representative Materials](#engineering-screening-and-representative-materials)
7. [Installation](#installation)
8. [Training and Generation](#training-and-generation)
9. [Evaluation](#evaluation)
10. [Reproducibility](#reproducibility)
11. [Documentation and Supplementary Results](#documentation-and-supplementary-results)
12. [Citation and License](#citation-and-license)

---

## Overview

DFCA addresses a fundamental challenge in computational materials design: generating stable, novel two-dimensional (2D) crystal structures. Unlike bulk 3D crystals where all lattice directions have similar physical meaning, 2D slab crystals exhibit distinct anisotropic behavior:

- **In-plane (XY):** Chemical bonding, periodic structure, atomic arrangement
- **Out-of-plane (Z):** Vacuum padding, slab thickness, layer stacking

DFCA explicitly models this anisotropy through separate neural network architectures, noise scaling, and physics-based training constraints.

---

## Key Contributions

1. **Anisotropic CrystalDiT Architecture**: Dual-stream cross-attention with separate XY and Z feature processing
2. **Physics-Informed Training**: 11 physical constraints enforcing structural validity during training
3. **Multi-Stage Screening Pipeline**: From composition filtering to phonon stability validation
4. **First-Principles Validation**: GPAW DFT verification of dynamically stable candidates

---

## Architecture

### CrystalDiT with Anisotropic Treatment

```
Input Crystal Structure (CIF)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Crystal Representation                                         │
│  ├─ Element encoding: atomic number → (period, group)          │
│  ├─ Lattice normalization: XY linear, Z MLP                     │
│  └─ Coordinate convention: fractional, Z-centered              │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  CrystalDiT (Diffusion Transformer)                             │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐   │
│  │   Lattice   │────▶│   DualStream │────▶│   BondDecoupled │   │
│  │  Embedder   │     │  CrossAttn   │     │      MLP        │   │
│  │ (XY/Z sep)  │     │             │     │                 │   │
│  └─────────────┘     └─────────────┘     └─────────────────┘   │
│                                                                 │
│  XY Stream: Linear embedder, larger noise scale (0.341)         │
│  Z  Stream: MLP embedder, smaller noise scale (0.113)           │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  CrystalGaussianDiffusion                                       │
│  ├─ DDPM with 1000 timesteps                                    │
│  ├─ Separate Z noise scaling (anisotropic)                      │
│  └─ Physics constraint losses                                   │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
Generated Crystal Structures (CIF)
```

### Key Architectural Features

| Component | Description |
|-----------|-------------|
| **Lattice Embedder** | Linear layer for XY lattice vectors; MLP for Z coordinate |
| **Atom Embedder** | Linear layer for XY atom features; MLP for Z features |
| **DualStream Cross-Attention** | Separate attention pathways for XY and Z features |
| **BondDecoupledMLP** | Independent processing of bond angle and distance features |
| **Anisotropic Noise Scaling** | Z noise scale (0.113) vs XY noise scale (0.341) |

Implementation: [`dfca/models/dit.py`](dfca/models/dit.py), [`dfca/diffusion/gaussian.py`](dfca/diffusion/gaussian.py)

---

## Physics-Informed Training

### Training-Stage Physical Constraints

Physical constraints are applied **only during training** as loss terms (gradient flows to model). They are **not** applied during inference.

| # | Constraint | Purpose | Decay Range |
|---|------------|---------|-------------|
| 1 | Invalid Slot | Push invalid positions to -1.0 | 0-70% |
| 2 | Soft Atom Count | Match atom count per sample | 0-70% |
| 3 | Row/Column Validity | L1 distance to valid elements | 30-70% |
| 4 | Slab Center | Z-direction center alignment | 0-70% |
| 5 | Slab Spread | Physical thickness constraint (≤3Å) | 0-70% |
| 6 | Lattice Length | Axis-weighted relative error | 0-70% |
| 7 | Lattice Angle | α, β ≈ 90°; γ ∈ [60°, 125°] | 0-70% |
| 8 | Element Count Distribution | Unique element count matching | No decay |
| 9 | Mass Density | Density alignment (g/cm³) | 0-70% |
| 10 | c-Length Floor | Minimum vacuum thickness (≥15Å) | 0-70% |
| 11 | c-Length Ceiling | Maximum vacuum thickness limit | 0-70% |

### Dynamic Weight Decay

```
Constraint Weight
      │
  1.0 ├───────────────────────────────────── ElemCount (no decay)
      │  ════════════════════════════════
      │
  d_m ├────────────╲  (decay_mid = 0.01)
      │             ╲_______________________
      │
  0.0 ├──────────────────────────────────────────────────────▶
      └─────────────┬─────────────────┬────────────────── Progress
                   30%               70%                 100%
```

Implementation: [`dfca/training/constraints.py`](dfca/training/constraints.py)

---

## Benchmark Results

### Generation Quality Comparison

Evaluated on 2D crystal generation benchmark using validity, uniqueness, novelty, and stability metrics.

| Model | Overall Validity | Uniqueness | Novelty (Formula) | 2D-UN |
|-------|-----------------|------------|-------------------|-------|
| CrystalDiT | — | — | — | — |
| **DFCA** | — | — | — | — |
| DiffCSP | — | — | — | — |
| DiffCSP++ | — | — | — | — |
| FlowMM | — | — | — | — |

*Note: Performance metrics will be populated upon completion of benchmark evaluation with trained checkpoint.*

### Screening Pipeline Results

From an initial batch of **5,000** generated structures:

| Stage | Filtered | Passed |
|-------|----------|--------|
| Generation | — | 5,000 |
| S0: Composition | Element restrictions | — |
| S1: Geometry | Vacuum, thickness, bonds | — |
| S2: Symmetry | Layer group validation | — |
| S3: Deduplication | Structure similarity | — |
| S3.5: ML Relaxation | MACE-MP-0 | — |
| S-dim: Dimensionality | 2D connectivity | — |
| S3T: Thermodynamic | E_above_hull | — |
| S5: Phonon Stability | No imaginary freq. | 89 |

**89 structures** passed the full screening pipeline, of which **19** were selected for first-principles validation.

Implementation: [`dfca/screening/pipeline.py`](dfca/screening/pipeline.py)

---

## Engineering Screening and Representative Materials

### Three-Stage Pipeline

```
Training Physical Constraints (Stage 1)
         │
         │  Only during training as loss terms
         │  Gradient flows to model parameters
         ▼
Generated Structures (Stage 2: Post-Processing Screening)
         │
         │  S0-S3T: Fast filters (CPU + ML)
         │  S5: Phonon stability (MACE-MP-0)
         ▼
DFT Candidates (Stage 3: First-Principles Validation)
         │
         │  M1: Structure relaxation (GPAW + PBE)
         │  M2: Elastic constants
         │  M3: Phonon dispersion
         ▼
Validated 2D Materials
```

### Representative 2D Crystals

Three representative materials validated through the complete pipeline:

| Material | Formula | Structure | Band Gap | DOS | Phonon |
|----------|---------|-----------|----------|-----|--------|
| Barium sulfide | BaS | rocksalt-derived | See supplement | See supplement | Stable |
| Barium selenide | BaSe₃ | layered | See supplement | See supplement | Stable |
| Silver selenide | Ag₂Se₅ | complex | See supplement | See supplement | Stable |

*Full structural, electronic (band structure), and vibrational (phonon DOS) results available in supplementary materials.*

### Complete Material List

The full set of **19 validated materials** includes:

Ag₂Se₅, Ba₃Te₃S₈, Ba₅(P₂S₅)₂, BaS, BaSe₃, Bi₂Te₃, Ca₂Te₄PF₂, CrTe₅, Cu, Hf₄Se₂S₃Br₅, HgTeS, Nb₂Te₇Pt, Nb₃Te₂, Nb₄Se₉, Sn₂Te, Ta₄FeSe₇, TaTe₂As, Zr, Zr₆Nb₂(Se₃I)₃

See [docs/supplementary/materials_index.md](docs/supplementary/materials_index.md) for detailed results including:
- Crystal structures (CIF files)
- Electronic band structures
- Phonon dispersion relations
- Elastic constants
- Formation energies

---

## Installation

### Requirements

- Python ≥ 3.10
- CUDA-capable GPU (for training and generation)
- 16GB+ RAM
- ~50GB storage

### Quick Setup

```bash
# Create conda environment
conda env create -f environment/environment-ml.yml
conda activate dfca

# Install package
pip install -e .
```

For DFT validation environment, see [`environment/environment-dft.yml`](environment/environment-dft.yml).

See [`docs/data.md`](docs/data.md) for dataset preparation instructions.

---

## Training and Generation

### Training

```bash
PYTHONPATH=. python scripts/train.py \
    --config configs/train.yaml \
    --data_dir ./Data \
    --output_dir ./output
```

Training requires the Merged-2D dataset (C2DB + 2DMatPedia, 17,654 structures). See [`docs/data.md`](docs/data.md) for dataset preparation.

### Generation

```bash
PYTHONPATH=. python scripts/generate.py \
    --config configs/generate.yaml \
    --checkpoint /path/to/checkpoint \
    --output_dir ./candidates \
    --num_samples 100 \
    --device cuda
```

Detailed documentation: [`docs/generation.md`](docs/generation.md)

---

## Evaluation

### Core Metrics

```bash
PYTHONPATH=. python eval/run_2d_eval.py \
    --gen_dir ./candidates \
    --train_csv ./Data/train.csv \
    --output_dir ./eval_results
```

Metrics computed:
- **Validity**: Structural, compositional, 2D geometric validity
- **Uniqueness**: Structure deduplication via RMSD matching
- **Novelty**: Comparison against training set
- **2D-UN**: Combined valid + unique + novel rate

### Stability Assessment

```bash
PYTHONPATH=. python eval/eval_2d_stability.py \
    --details_csv ./eval_results/core_details.csv \
    --mp_hull_path /path/to/mp_hull.pkl \
    --output_dir ./eval_results/stability
```

Uses CHGNet for surrogate stability assessment (E_above_hull).

---

## Reproducibility

### Configuration Files

All parameters are configurable via YAML files:

```bash
# Training configuration
configs/train.yaml

# Generation configuration  
configs/generate.yaml

# Screening pipeline
configs/screening.yaml

# DFT validation
configs/dft_validation.yaml
```

### Random Seed

```bash
python scripts/train.py --config configs/train.yaml --seed 42
```

See [`docs/randomness_and_reproducibility.md`](docs/randomness_and_reproducibility.md) for detailed seed management.

### Testing

```bash
# Run all CPU tests
PYTHONPATH=. pytest tests/unit/ -v

# Run regression tests
PYTHONPATH=. pytest tests/regression/ -v
```

See [`docs/testing.md`](docs/testing.md) for full test matrix.

### Reproducing the Paper

| Stage | Command | Requirements |
|-------|---------|--------------|
| 1. Training | `scripts/train.py` | GPU, Merged-2D dataset |
| 2. Generation | `scripts/generate.py` | Trained checkpoint |
| 3. Screening | `scripts/screen.py` | MACE-MP-0 checkpoint |
| 4. DFT Validation | `scripts/validate_dft.py` | HPC cluster, GPAW |

**Note:** CPU quickstart (`python examples/cpu_quickstart.py`) is a software smoke test only. It does not evaluate generation quality or reproduce paper results.

---

## Documentation and Supplementary Results

### Core Documentation

| Document | Description |
|----------|-------------|
| [`docs/method.md`](docs/method.md) | Scientific method and architecture details |
| [`docs/training.md`](docs/training.md) | Training pipeline and loss functions |
| [`docs/generation.md`](docs/generation.md) | Generation workflow |
| [`docs/screening.md`](docs/screening.md) | Multi-stage screening pipeline |
| [`docs/dft_validation.md`](docs/dft_validation.md) | GPAW DFT validation protocol |
| [`docs/representation.md`](docs/representation.md) | Crystal representation |
| [`docs/data.md`](docs/data.md) | Dataset provenance (Merged-2D) |
| [`docs/randomness_and_reproducibility.md`](docs/randomness_and_reproducibility.md) | Reproducibility details |

### Supplementary Materials

| Resource | Location |
|----------|----------|
| Material results | [`docs/supplementary/materials_index.md`](docs/supplementary/materials_index.md) |
| Representative structures | [`result/representative_structures/`](result/representative_structures/) |
| Screening results | [`result/passed_screen.csv`](result/passed_screen.csv) |

---

## Citation and License

### Citation

If you use DFCA in your research, please cite:

```
TODO: Update upon publication
```

### Third-Party Code

DFCA builds upon several open-source projects:

- **GaussianDiffusion**: Modified from OpenAI's ADM/IDDPM/GLIDE ([GitHub](https://github.com/openai/guided-diffusion))
- **DiT Architecture**: Based on Peebles & Xie ([arXiv:2203.01917](https://arxiv.org/abs/2203.01917))
- **MACE-MP-0**: ML interatomic potential ([mace-offential](https://github.com/ACEsuit/mace-offential))
- **GPAW**: DFT calculations ([gpaw.github.io](https://gpaw.github.io/))

See [`THIRD_PARTY.md`](THIRD_PARTY.md) for detailed acknowledgments.

### License

Licensing terms are being finalized prior to public release. See [`LICENSE`](LICENSE) file for current status.

---

## Acknowledgments

- C2DB (Computational 2D Materials Database)
- OpenAI for diffusion model infrastructure
- MACE potential authors
- GPAW developers
- pymatgen developers
