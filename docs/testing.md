# Testing Documentation

**Generated:** 2026-10-06  
**Purpose:** Publication-release audit verification

---

## Completed Release Tests

The following tests were successfully executed during the publication-release audit:

### Python Compilation

```bash
python -m compileall -q dfca diffusion scripts examples tests
```
**Result:** All modules compile successfully (no syntax errors)

### Unit and Regression Tests

```bash
pytest -q
```
**Result:** 80 tests passed, 0 failed

| Test Category | Tests | Passed | Failed | Skipped |
|---------------|-------|--------|--------|---------|
| Unit tests (representation) | 23 | 23 | 0 | 0 |
| Unit tests (model) | 10 | 10 | 0 | 0 |
| Regression tests (diffusion) | 10 | 10 | 0 | 0 |
| Config equivalence tests | 22 | 22 | 0 | 0 |
| Screening tests | 15 | 15 | 0 | 0 |
| **Total** | **80** | **80** | **0** | **0** |

### CLI Smoke Tests

| Command | Result |
|---------|--------|
| `python scripts/train.py --help` | ✅ PASS |
| `python scripts/generate.py --help` | ✅ PASS |
| `python scripts/screen.py --help` | ✅ PASS |
| `python scripts/validate_dft.py --help` | ✅ PASS |

### CPU Quick Start

```bash
PYTHONPATH=. python examples/cpu_quickstart.py
```
**Result:** ✅ PASS (0.078s)

| Component | Status |
|-----------|--------|
| CIF parsing | ✅ PASS |
| DFCA representation | ✅ PASS |
| Model construction | ✅ PASS |
| CPU forward smoke test | ✅ PASS |

### ML Dependencies Smoke Tests

| Test | Result |
|------|--------|
| `import torch_dftd` | ✅ PASS |
| MACE-MP-0 + D3 (import) | ✅ PASS |
| GPAW (single-core, import) | ✅ PASS |

---

## Tests NOT Executed in Release Audit

The following tests were **NOT** executed during the release audit due to resource constraints:

### GPU-Dependent Tests
- Training on GPU
- Generation with trained checkpoint
- Multi-GPU training/generation

### HPC/DFT Tests
- **MPI/multi-rank GPAW validation** — Not tested (requires HPC cluster)
- Single-rank GPAW DFT validation
- Phonon dispersion calculations
- Elastic constant calculations

### Expensive Scientific Tests
- Full paper generation quality evaluation
- Checkpoint-based generation reproducibility
- End-to-end screening pipeline
- MACE relaxation stress tests

---

## Test Categories

### 1. Automated Unit/Regression Tests
These run automatically and verify code correctness:
- Representation constants and functions
- Model architecture and forward pass
- Diffusion process behavior
- Configuration loading
- Screening stage logic

**Environment:** CPU only (no GPU required)

### 2. Smoke Tests
These verify that key components can be imported and execute:
- CLI help text
- CPU quickstart
- ML library imports
- Calculator initialization

**Environment:** CPU only

### 3. Scientific Reproduction Tests
These verify that paper results can be reproduced:
- GPU training with documented configuration
- Generation from trained checkpoint
- DFT validation with GPAW
- Phonon stability calculations

**Environment:** Requires GPU + HPC cluster with GPAW

### 4. Tests Not Executed
These exist in the codebase but were not run during the release audit:
- Multi-rank MPI tests
- Long-running MD simulations
- Full paper evaluation pipelines

---

## Reproducibility Notes

### What the CPU Quickstart Tests
- CIF file parsing
- DFCA representation conversion
- Model construction and initialization
- CPU forward pass execution

### What the CPU Quickstart Does NOT Test
- Generation quality (requires trained checkpoint)
- Training convergence (requires GPU and dataset)
- Scientific accuracy (requires DFT validation)

### Full Paper Reproduction Requirements
To reproduce paper results:

1. **Training:** GPU environment with CUDA, documented in `environment/environment-ml.yml`
2. **Generation:** Trained checkpoint (not distributed; must be trained first)
3. **Screening:** GPU environment with MACE-MP-0 installed
4. **DFT Validation:** HPC cluster with GPAW and MPI

---

## Quick Test Commands

```bash
# Run all unit tests (fast, no GPU required)
PYTHONPATH=. python -m pytest tests/unit/ -q

# Run all regression tests (may require GPU for some)
PYTHONPATH=. python -m pytest tests/regression/ -q

# Run config equivalence tests
PYTHONPATH=. python -m pytest tests/test_config_equivalence.py -q

# Run all tests
PYTHONPATH=. python -m pytest tests/ -q

# Run CPU quickstart
PYTHONPATH=. python examples/cpu_quickstart.py

# Verify all modules compile
python -m compileall -q dfca diffusion scripts examples tests
```

---

## Key Scientific Values Verified

The following scientific constants were verified to match across all configuration sources:

| Parameter | Value | Location | Status |
|-----------|-------|----------|--------|
| MAX_LATTICE_LENGTH | 46.7425 | representation.py | ✅ VERIFIED |
| z_noise_scale | 0.113001 | gaussian.py | ✅ VERIFIED |
| lattice_c_noise_scale | 0.340659 | gaussian.py | ✅ VERIFIED |
| lattice_loss_z_weight | 0.706323 | gaussian.py | ✅ VERIFIED |
| ATOM_XY_FEATURE_WEIGHTS | [1.5, 2.0, 1.0, 1.0] | gaussian.py | ✅ VERIFIED |
| ATOM_Z_LOSS_WEIGHT | 0.1 | gaussian.py | ✅ VERIFIED |
| ATOM_TOTAL_LOSS_COMBINE_WEIGHT | 15.9768 | gaussian.py | ✅ VERIFIED |
| DECAY_BOUNDARY_MID | 0.30 | constraints.py | ✅ VERIFIED |
| DECAY_BOUNDARY_LATE | 0.70 | constraints.py | ✅ VERIFIED |
| MIN_VACUUM_THICKNESS | 15.0 | constraints.py | ✅ VERIFIED |
| z_from_xy_init | 0.782159 | attention.py | ✅ VERIFIED |
| xy_from_z_init | 0.1 | attention.py | ✅ VERIFIED |

---

## Known Limitations

### Current Environment (Release Audit)
- CPU only (no GPU available)
- MACE-MP-0 installed (for import testing)
- GPAW installed (single-core, for import testing)
- No MPI configured

### What This Means for Users
- **GPU tests:** NOT RUN (requires GPU hardware)
- **MPI/GPAW tests:** NOT RUN (requires HPC cluster)
- **Generation quality:** Cannot be assessed without trained checkpoint

---

*Last updated: 2026-10-06*
