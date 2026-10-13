# Final Dependency Audit

**Date:** 2026-10-02  
**Status:** HISTORICAL AUDIT RECORD — This file documents dependency verification as of 2026-10-02.
For current release status, see FINAL_PUBLICATION_RELEASE_AUDIT.md.

## 1. Actual Runtime Dependencies

Scanned all Python files in the repository to determine direct runtime dependencies.

| Dependency | Required by | Environment | Version Known? | Notes |
|------------|-------------|-------------|----------------|-------|
| `torch` | 41 imports | environment-ml.yml, environment-hpc.yml | ✅ pytorch>=2.0 | Core ML framework |
| `numpy` | 40 imports | All environments | ✅ numpy>=1.24 | Scientific computing |
| `timm` | 2 imports | environment-ml.yml, environment-hpc.yml | ⚠️ Unpinned | DiT components (PatchEmbed, Attention, Mlp) |
| `pymatgen` | 14 imports | environment-ml.yml, environment-dft.yml, environment-hpc.yml | ✅ pymatgen>=2023 | Structure handling |
| `yaml` / `PyYAML` | 1 import | All environments | ✅ pyyaml>=6.0 | Config loading |
| `mace-torch` | Mentioned | environment-ml.yml, environment-hpc.yml | ✅ mace-torch>=0.3 | ML relaxation (S3.5) |
| `e3nn` | Mentioned | environment-ml.yml, environment-hpc.yml | ✅ e3nn>=0.5 | Equivariant operations |
| `gpaw` | Mentioned | environment-dft.yml, environment-hpc.yml | ✅ gpaw>=24.6 | DFT validation |
| `ase` | Mentioned | environment-dft.yml, environment-hpc.yml | ✅ ase>=3.22 | Atomic structure |
| `phonopy` | Mentioned | environment-dft.yml, environment-hpc.yml | ✅ phonopy>=2.18 | Phonon calculations |
| `mpi4py` | Mentioned | environment-dft.yml, environment-hpc.yml | ✅ mpi4py>=3.1 | Parallel computing |
| `openmpi` | Mentioned | environment-dft.yml, environment-hpc.yml | ✅ openmpi>=4.1 | MPI runtime |
| `spglib` | Listed | environment-ml.yml, environment-hpc.yml | ✅ spglib | Symmetry |
| `monty` | Listed | All environments | ✅ monty>=2023 | Serialization |
| `scipy` | Listed | All environments | ✅ scipy>=1.10 | Scientific computing |
| `pandas` | Listed | environment-ml.yml, environment-hpc.yml | ✅ pandas>=2.0 | Data processing |
| `matplotlib` | Listed | All environments | ✅ matplotlib>=3.7 | Visualization |
| `h5py` | Listed | All environments | ✅ h5py>=3.8 | Data format |
| `tqdm` | Listed | environment-ml.yml, environment-hpc.yml | ✅ tqdm>=4.65 | Progress bars |
| `pytest` | Testing | All environments | ✅ pytest>=7.0 | Testing framework |

## 2. Dependencies NOT Found in Code

The following packages are listed in environment files but have no direct imports in the current source code:

| Dependency | Environment | Status |
|------------|-------------|--------|
| `torchaudio` | environment-ml.yml | Not used |
| `cuda-toolkit` | Both | Build dependency |
| `sympy` | environment-ml.yml, environment-hpc.yml | Not used |
| `seekpath` | environment-dft.yml | Listed but not imported |
| `emmet-core` | environment-dft.yml | Optional API dependency |
| `psutil` | environment-hpc.yml | HPC utilities |
| `black`, `ruff` | environment-ml.yml | Development tools |

## 3. timm Version Note

**Historical timm version requires verification.**

The current environment files use `timm` without an exact version pin because:
- The exact historical version used during validation is not definitively established
- `timm` has had breaking changes between versions affecting DiT components
- Without verification, specifying an exact version could cause false failures

Users should verify `timm` compatibility with their environment if using DiT components directly.

## 4. Environment Separation

Three separate environments are maintained:

| Environment | Purpose | Key Components |
|-------------|---------|----------------|
| `environment-ml.yml` | Training, generation, screening | PyTorch, timm, pymatgen, MACE |
| `environment-dft.yml` | GPAW DFT validation | GPAW, ASE, phonopy, MPI |
| `environment-hpc.yml` | Multi-node GPU cluster | PyTorch + DFT combined |

Do NOT combine all dependencies into one environment unless validated.

## 5. Package Installation

To use the package:

```bash
# ML environment
conda env create -f environment/environment-ml.yml
conda activate dfca-ml

# DFT environment (separate)
conda env create -f environment/environment-dft.yml
conda activate dfca-dft

# Install package in editable mode
pip install -e .
```

## 6. Verified Import Paths

All imports are relative to repository root with PYTHONPATH set, or via installed package.
