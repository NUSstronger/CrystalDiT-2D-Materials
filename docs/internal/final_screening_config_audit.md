# Final Screening Configuration Audit

**Date:** 2026-10-02  
**Status:** HISTORICAL AUDIT RECORD — This file documents screening config verification as of 2026-10-02.
For current release status, see FINAL_PUBLICATION_RELEASE_AUDIT.md.

## Summary

All screening scientific defaults are consistent between:
- `configs/screening.yaml`
- `dfca/screening/config.py` (ScreeningConfig dataclass)

## Scientific Screening Default Mismatches: 0

## Verification Table

| Parameter | configs/screening.yaml | ScreeningConfig | Status |
|-----------|------------------------|-----------------|--------|
| vacuum_min_angstrom | 5.0 | 5.0 | ✅ |
| slab_thickness_max | 15.0 | 15.0 | ✅ |
| min_bond_distance | 0.4 | 0.4 | ✅ |
| lattice_ab_min | 1.0 | 1.0 | ✅ |
| lattice_ab_max | 50.0 | 50.0 | ✅ |
| ltol | 0.30 | 0.30 | ✅ |
| stol | 0.30 | 0.30 | ✅ |
| angle_tol | 10.0 | 10.0 | ✅ |
| symprec | 0.1 | 0.1 | ✅ |
| relax_fmax | 0.05 | 0.05 | ✅ |
| relax_steps | 400 | 400 | ✅ |
| relax_steps_retry | 800 | 800 | ✅ |
| fix_z_lattice | true | True | ✅ |
| elastic_delta | 0.005 | 0.005 | ✅ |
| skip_phonon | false | False | ✅ |
| phonon_supercell | [3, 3, 1] | [3, 3, 1] | ✅ |
| phonon_displacement | 0.03 | 0.03 | ✅ |
| phonon_mesh | [20, 20, 1] | [20, 20, 1] | ✅ |
| imaginary_freq_tol | -0.02 | -0.02 | ✅ |
| ehull_threshold_ml | 0.2 | 0.2 | ✅ |
| enable_hard_ehull_gate | false | False | ✅ |
| enable_md | false | False | ✅ |
| md_temperature | 300.0 | 300.0 | ✅ |
| md_dt_fs | 1.0 | 1.0 | ✅ |
| md_s7a_steps | 3000 | 3000 | ✅ |
| md_s7b_steps | 10000 | 10000 | ✅ |
| vasp_vacuum_angstrom | 20.0 | 20.0 | ✅ |

## Conclusion

All screening scientific parameters are verified consistent. No changes required.
