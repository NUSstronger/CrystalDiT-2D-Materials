# DFCA Scientific Code Freeze Report

**Date:** 2026-10-02  
**Status:** HISTORICAL AUDIT RECORD — This file documents the code freeze state as of 2026-10-02.
For current release status, see FINAL_PUBLICATION_RELEASE_AUDIT.md.

---

## Scientific Integrity

| Category | Count | Notes |
|----------|-------|-------|
| Intentional scientific algorithm changes | 0 | No changes to model, diffusion, training, screening, validation |
| Scientific parameter changes | 0 | No changes to configs, defaults, thresholds |
| Screening default mismatches | 0 | configs/screening.yaml ↔ ScreeningConfig verified consistent |
| GPAW default mismatches | 0 | configs/dft_validation.yaml ↔ GPAWConfig verified consistent |

---

## Tests

| Metric | Value |
|--------|-------|
| Collected | 80 |
| Passed | 80 |
| Skipped | 0 |
| Failed | 0 |
| Errors | 0 |
| Scientific failures | 0 |
| Environment failures | 0 |

**Note:** Initial test runs showed failures due to missing packages (torch, timm, pymatgen, ase, phonopy) in base environment. After installing required packages, all 80 tests passed.

---

## CLI

| Script | Status |
|--------|--------|
| train.py --help | ✅ PASS |
| generate.py --help | ✅ PASS |
| screen.py --help | ✅ PASS |
| validate_dft.py --help | ✅ PASS |

---

## Paths

| Category | Count |
|----------|-------|
| Personal executable paths | 0 |

**Audit file:** `docs/internal/final_path_audit.md`

---

## Dependencies

| Dependency | Environment | Status |
|------------|-------------|--------|
| timm | environment-ml.yml, environment-hpc.yml | ✅ ADDED (was missing) |
| pymatgen | All environments | ✅ Present |
| MACE software | environment-ml.yml, environment-hpc.yml | ⚠️ LICENSE VERIFICATION REQUIRED |
| MACE model | N/A | ⚠️ LICENSE VERIFICATION REQUIRED |
| GPAW | environment-dft.yml, environment-hpc.yml | ✅ Present |
| MPI | environment-dft.yml, environment-hpc.yml | ✅ Present |

**Dependency audit file:** `docs/internal/final_dependency_audit.md`

---

## Packaging

| Category | Count |
|----------|-------|
| __pycache__ | 0 |
| *.pyc | 0 |
| .pytest_cache | 0 |
| .DS_Store | 0 |
| __MACOSX | 0 |
| Broken README links | 0 |

**Package file:** `pyproject.toml` created for editable installation

---

## Licensing

| Component | Status |
|-----------|--------|
| DFCA | ⚠️ AUTHOR DECISION REQUIRED |
| DiT (Peebles & Xie) | ✅ BSD License |
| OpenAI diffusion (ADM/IDDPM/GLIDE) | ✅ MIT License |
| MACE software | ⚠️ VERIFICATION REQUIRED BEFORE PUBLIC RELEASE |
| MACE pretrained model | ⚠️ VERIFICATION REQUIRED BEFORE PUBLIC RELEASE |
| GPAW | ✅ GPLv3 |
| ASE | ✅ LGPLv3 |
| phonopy | ✅ BSD License |
| pymatgen | ✅ MIT License |

---

## Artifacts

| Artifact | Status |
|----------|--------|
| checkpoint | ⏳ PENDING — External release with manuscript |
| checkpoint SHA256 | TODO — Will be calculated when checkpoint retrieved |
| DFT/phonon artifacts | ⏳ PENDING HPC RETRIEVAL |
| training curves | NOT REQUIRED FOR PAPER REPRODUCIBILITY |

---

## Frozen Paths

Scientific freeze covers:

- `dfca/`
- `diffusion/`
- `configs/`

---

## Changes Allowed Without Scientific Regression

Only clearly non-behavioral items:

- README typo
- citation metadata
- external artifact URL
- DOI
- LICENSE metadata (when finalized)
- formatting outside scientific code

---

## Final Classification

### CODE-FREEZE READY

Scientific source is fully frozen and verified:
- ✅ Scientific failures = 0
- ✅ Collection errors = 0
- ✅ Broken production imports = 0
- ✅ Scientific config mismatches = 0
- ✅ Personal executable paths = 0

### PUBLIC RELEASE BLOCKED BY

- ⚠️ DFCA LICENSE not finalized
- ⚠️ MACE LICENSE not verified
- ⚠️ Pretrained checkpoint not archived with SHA256
- ⚠️ DFT/phonon artifacts pending HPC retrieval

---

*Report generated: 2026-10-02*
