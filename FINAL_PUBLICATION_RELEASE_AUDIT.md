# Final Publication Release Audit

**Date:** 2026-10-06  
**Paper:** Engineering Applications of Artificial Intelligence  
**Repository:** DFCA (Diffusion Framework for Crystal Anisotropy)

---

## Executive Summary

| Category | Status |
|----------|--------|
| Code Freeze | ✅ COMPLETE |
| Scientific Integrity | ✅ VERIFIED |
| Documentation Consistency | ✅ FIXED |
| Tests | ✅ 93 PASSED |
| CLI | ✅ ALL PASS |
| Release Blockers | 4 REMAIN |

---

## 1. Files Changed

### Documentation Updates

| File | Change |
|------|--------|
| `docs/data.md` | Added Merged-2D dataset provenance (C2DB + 2DMatPedia, 17,654 structures), license verification checklist |
| `docs/screening.md` | Added paper-to-implementation stage mapping table (S0-S7 → Paper Stages) |
| `docs/testing.md` | Updated with actual test results (93 passed in 6.53s), documented executed vs not-executed tests |
| `docs/method.md` | Updated dataset reference from "C2DB" to "Merged-2D (C2DB + 2DMatPedia, 17,654 structures)" |
| `README.md` | Changed data description, added "Reproducing the Paper" section with 4-stage workflow |
| `docs/internal/*.md` | Marked all internal audit files as "HISTORICAL AUDIT RECORD" |

### Scientific Code

| File | Status |
|------|--------|
| `dfca/` | No changes (code frozen) |
| `diffusion/` | No changes (code frozen) |
| `configs/` | No changes (code frozen) |
| `scripts/` | No changes (code frozen) |

---

## 2. Documentation Inconsistencies Fixed

### 2.1 Dataset Description (FIXED)
- **Before:** README and method docs only mentioned "C2DB"
- **After:** Updated to "Merged-2D (C2DB + 2DMatPedia, 17,654 structures)"
- **Files:** `README.md`, `docs/method.md`, `docs/data.md`

### 2.2 Stage Mapping (FIXED)
- **Issue:** Implementation stages (S0-S7) did not align with paper stage terminology
- **Fix:** Added comprehensive mapping table to `docs/screening.md`
- **Key mappings:**
  - ML Relaxation → S3.5 (MACE-MP-0 only)
  - Phonon Stability → S5 (phonopy + MACE forces)
  - DFT Validation → M1-M4 (GPAW)

### 2.3 Test Documentation (FIXED)
- **Before:** Testing documentation did not reflect actual test execution
- **After:** Documented 93-pass result, CLI tests, and explicitly listed NOT-executed tests

---

## 3. Paper-Code Consistency Checks

### 3.1 Dataset (VERIFIED)
| Property | Paper Claim | Implementation | Status |
|----------|-------------|----------------|--------|
| Source | C2DB + 2DMatPedia | Merged-2D | ✅ |
| Size | 17,654 structures | 17,654 structures | ✅ |
| Filtering | 2D materials only | 2D filter applied | ✅ |

### 3.2 MLIP (VERIFIED)
| Property | Paper Claim | Implementation | Status |
|----------|-------------|----------------|--------|
| MLIP | MACE-MP-0 only | MACE-MP-0 only | ✅ |
| Fallback chain | None | None | ✅ |
| Usage stages | ML relaxation, phonons | S3.5, S5 | ✅ |

### 3.3 Model Parameters (VERIFIED)
| Parameter | Value | Locations Verified |
|-----------|-------|-------------------|
| z_noise_scale | 0.113001 | configs/model.yaml, dfca/model/config.py |
| lattice_c_noise_scale | 0.340659 | configs/model.yaml, dfca/model/config.py |
| z_from_xy_init | 0.782159 | configs/model.yaml, dfca/model/config.py |
| xy_from_z_init | 0.1 | configs/model.yaml, dfca/model/config.py |
| MAX_LATTICE_LENGTH | 46.7425 | dfca/model/normalizer.py |
| depth | 18 | configs/model.yaml, dfca/model/config.py |
| hidden_size | 512 | configs/model.yaml, dfca/model/config.py |
| num_heads | 8 | configs/model.yaml, dfca/model/config.py |

### 3.4 Screening Parameters (VERIFIED)
All parameters in `configs/screening.yaml` match `dfca/screening/config.py` (0 mismatches).

### 3.5 DFT/GPAW Parameters (VERIFIED)
All parameters in `configs/dft_validation.yaml` match `dfca/validation/config.py` (0 mismatches).

---

## 4. Tests Executed and Results

### 4.1 Compilation
```bash
python -m compileall -q dfca diffusion scripts examples tests
```
**Result:** ✅ PASS

### 4.2 Unit Tests
```bash
pytest -q
```
**Result:** ✅ 93 passed in 6.53s

### 4.3 CPU Quickstart
```bash
python examples/cpu_quickstart.py
```
**Result:** ✅ PASS (0.065s)  
**Note:** CPU forward pass is a software/API smoke test only. Does not evaluate generation quality.

### 4.4 CLI Help Tests
| Command | Result |
|---------|--------|
| `python scripts/train.py --help` | ✅ PASS |
| `python scripts/generate.py --help` | ✅ PASS |
| `python scripts/screen.py --help` | ✅ PASS |
| `python scripts/validate_dft.py --help` | ✅ PASS |

---

## 5. Tests NOT Executed

The following tests are NOT executed due to resource/environment requirements:

| Test | Reason Not Executed |
|------|---------------------|
| GPU training | Requires CUDA GPU |
| GPU generation | Requires CUDA GPU |
| Full screening pipeline | Requires MACE-MP-0 checkpoint |
| DFT validation (GPAW) | Requires MPI + GPAW + HPC environment |
| MPI parallel tests | Requires HPC cluster with OpenMPI |
| Scientific reproduction | Requires trained checkpoint + HPC |
| Phonon calculations | Requires MACE + phonopy + HPC |

---

## 6. Remaining External Dependencies

### 6.1 Verified Dependencies
| Package | License | Status |
|---------|---------|--------|
| pymatgen | MIT | ✅ OK |
| GPAW | GPLv3 | ✅ OK |
| ASE | LGPLv3 | ✅ OK |
| phonopy | BSD | ✅ OK |
| PyTorch | BSD | ✅ OK |
| numpy | BSD | ✅ OK |
| DiT (Peebles & Xie) | BSD | ✅ OK |
| OpenAI diffusion | MIT | ✅ OK |

### 6.2 Pending Verification
| Component | Issue | Action Required |
|-----------|-------|-----------------|
| **DFCA License** | Not finalized | Author decision required |
| **MACE software** | License verification required | Verify before public release |
| **MACE pretrained model** | License verification required | Verify before public release |
| **timm** | Not version-pinned | Historical version unknown |

---

## 7. Dataset and Checkpoint Availability

### 7.1 Training Dataset
- **Merged-2D:** C2DB + 2DMatPedia (17,654 structures)
- **Availability:** Users must obtain from original sources per their licenses
- **License checklist:** Provided in `docs/data.md`

### 7.2 Trained Checkpoint
- **Status:** ⏳ PENDING — External release with manuscript
- **SHA256:** TODO — Will be calculated when checkpoint retrieved

### 7.3 DFT/Phonon Artifacts
- **Status:** ⏳ PENDING HPC RETRIEVAL
- **Note:** Not required for paper reproducibility

### 7.4 Training Curves
- **Status:** NOT REQUIRED FOR PAPER REPRODUCIBILITY
- **Note:** Paper focuses on method and screening results, not training dynamics

---

## 8. License/Provenance Items Requiring Human Verification

| Item | Priority | Status |
|------|----------|--------|
| DFCA License | HIGH | ⚠️ Author decision required |
| MACE software license | HIGH | ⚠️ Verify before public release |
| MACE model license | HIGH | ⚠️ Verify before public release |
| timm version pinning | MEDIUM | ⚠️ Verify compatibility |
| C2DB data license | HIGH | ⚠️ User responsibility (per docs/data.md) |
| 2DMatPedia data license | HIGH | ⚠️ User responsibility (per docs/data.md) |

---

## 9. Release Readiness Checklist

| Requirement | Status |
|-------------|--------|
| Scientific code frozen | ✅ |
| Scientific parameters verified | ✅ |
| Documentation consistent | ✅ |
| Personal paths removed | ✅ |
| Release artifacts cleaned | ✅ |
| Tests passing | ✅ |
| CLI functional | ✅ |
| DFCA license finalized | ⚠️ |
| MACE license verified | ⚠️ |
| Checkpoint archived with SHA256 | ⏳ |
| DFT artifacts retrieved | ⏳ |

---

## 10. Release Blockers

### Must Resolve Before Public Release

1. **DFCA License** — Not finalized; author must decide on license type
2. **MACE License Verification** — Both software and model require license verification
3. **Trained Checkpoint** — Must be archived with SHA256 hash
4. **timm Version Pinning** — Historical version unknown, may cause compatibility issues

---

## 11. Audit Methodology

This audit followed a conservative approach:
- ✅ Only changed documentation, not scientific implementation
- ✅ Verified all configuration values match across files
- ✅ Marked internal audit files as historical
- ✅ Documented all tests executed and not executed
- ✅ Preserved all original scientific defaults

---

*Audit completed: 2026-10-06*
