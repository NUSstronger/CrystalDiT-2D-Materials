# DFT Validation

First-principles validation using GPAW density functional theory.

## Overview

Screened candidates undergo three stages of DFT validation:

```
Screened Candidates → M1: Relaxation → M2: Elastic Constants → M3: Phonon Dispersion
```

## Stage M1: Structure Relaxation

### Purpose
Find the ground-state structure (minimum energy configuration).

### Method
- **DFT code:** GPAW
- **Functional:** PBE (Perdew-Burke-Ernzerhof)
- **Basis:** Plane-wave GPAW
- **Convergence:** Force < 0.05 eV/Å

### Parameters

| Parameter | Value | Reference |
|-----------|-------|-----------|
| Functional | PBE | GGA-PBE |
| K-point density | 3.0 Å⁻¹ | Monkhorst-Pack |
| Plane-wave cutoff | 800 eV | Configurable |
| Force tolerance | 0.05 eV/Å | DFT standard |

**Reference:** [`dfca/validation/m1_relax.py`](dfca/validation/m1_relax.py)

### Output
- Relaxed structure (CIF)
- Total energy
- Force on each atom
- Stress tensor

## Stage M2: Elastic Constants

### Purpose
Characterize mechanical properties.

### Method
- **Finite difference:** Apply strain ε, compute stress σ
- **Elastic tensor:** C_ij = σ_i / ε_j
- **Symmetry:** Apply appropriate strains for 2D layer group

### Strains Applied

For 2D materials (hexagonal symmetry):

| Strain Type | Components | Constants |
|-------------|------------|-----------|
| Uniaxial | ε₁ | C₁₁ |
| Uniaxial | ε₂ | C₂₂ |
| Shear | ε₆ | C₆₆ |
| Biaxial | ε₁ = ε₂ | B (bulk modulus) |

### Output
- Elastic constants (GPa)
- Young's modulus
- Poisson's ratio
- Shear modulus

**Reference:** [`dfca/validation/m2_elastic.py`](dfca/validation/m2_elastic.py)

## Stage M3: Phonon Dispersion

### Purpose
Validate dynamic stability.

### Method
- **Force calculator:** GPAW (DFT)
- **Phonon code:** phonopy
- **Supercell:** 3×3×1 (configurable)
- **q-points:** High-symmetry path in 2D BZ

### Stability Criterion

A structure is dynamically stable if:
- No imaginary frequencies anywhere in BZ
- Minimum frequency at Γ > 0

For 2D materials:
- Acoustic modes should go to zero at Γ (in-plane and out-of-plane)
- Optical modes should be positive

### Output
- Phonon dispersion plot
- Phonon DOS
- Free energy vs temperature (optional)
- Dynamical matrix at Γ

**Reference:** [`dfca/validation/m3_phonon.py`](dfca/validation/m3_phonon.py)

## Configuration

DFT validation is configured via [`configs/dft_validation.yaml`](configs/dft_validation.yaml):

```yaml
m1_relaxation:
  functional: PBE
  kpoint_density: 3.0
  encut: 800
  force_tolerance: 0.05  # eV/Å
  max_iterations: 500

m2_elastic:
  strain_magnitudes: [0.01, 0.02, 0.03]
  symmetry: hexagonal

m3_phonon:
  supercell: [3, 3, 1]
  qpath: [[0, 0, 0], [1/3, 1/3, 0], [0.5, 0, 0], [0, 0, 0]]
```

## HPC Environment

DFT calculations require the dedicated HPC environment:

```bash
# Activate DFT environment
conda activate dfca-dft

# Submit job
sbatch submit_dft_validation.sh
```

**Reference:** [`environment/environment-dft.yml`](environment/environment-dft.yml)

## Software Stack

| Package | Version | Purpose |
|---------|---------|---------|
| GPAW | ≥24.6.0 | DFT calculations |
| ASE | ≥3.23.0 | Interface and file I/O |
| phonopy | ≥2.20.0 | Phonon calculations |
| numpy | ≥1.24 | Numerical operations |

## Hardware Requirements

| Stage | CPU Cores | Memory | Time |
|-------|-----------|--------|------|
| M1 | 16-64 | 32-64 GB | 1-10 hours |
| M2 | 16-64 | 32-64 GB | 2-20 hours |
| M3 | 16-64 | 64-128 GB | 5-30 hours |

Times depend on system size and convergence settings.

## MPI Parallelization

GPAW supports MPI parallelization:

```bash
# 4-node job
mpirun -n 4 gpaw python relax.py
```

Configuration in job scripts:
- K-point parallelization
- Domain decomposition
- BLAS/LAPACK threads

**Reference:** [`dfca/hpc/`](dfca/hpc/)

## Validation Workflow

```bash
# 1. Prepare structures
python prepare_validation.py --input ./screened --output ./validation_input

# 2. Submit M1 relaxation jobs
sbatch submit_m1.sh

# 3. Check convergence
python check_convergence.py --stage m1

# 4. Submit M2 elastic constants
sbatch submit_m2.sh

# 5. Submit M3 phonon calculation
sbatch submit_m3.sh

# 6. Generate final report
python generate_report.py --output ./validation_report
```

## Output Format

Validation results are stored in:

```
validation_results/
├── m1_relaxation/
│   ├── structure_001/
│   │   ├── relaxed.cif
│   │   ├── energy.json
│   │   └── CONVERGED
│   └── ...
├── m2_elastic/
│   ├── structure_001/
│   │   ├── elastic_constants.json
│   │   └── mechanical_properties.json
│   └── ...
├── m3_phonon/
│   ├── structure_001/
│   │   ├── band.yaml
│   │   ├── dos.dat
│   │   └── stability.json
│   └── ...
└── summary.json
```

---

*Last updated: 2026-10-01*
