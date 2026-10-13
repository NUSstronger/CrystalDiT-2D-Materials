# Final GPAW/DFT Configuration Audit

**Date:** 2026-10-02  
**Status:** HISTORICAL AUDIT RECORD — This file documents DFT config verification as of 2026-10-02.
For current release status, see FINAL_PUBLICATION_RELEASE_AUDIT.md.

## Summary

All GPAW DFT scientific parameters are consistent between:
- `configs/dft_validation.yaml`
- `dfca/validation/config.py` (GPAWConfig dataclass)

## GPAW Scientific Parameter Mismatches: 0

## Verification Table

| Parameter | configs/dft_validation.yaml | GPAWConfig | Status |
|-----------|----------------------------|------------|--------|
| encut | 550 | 550 | ✅ |
| xc | PBE | PBE | ✅ |
| fermi_smearing | 0.05 | 0.05 | ✅ |
| dk_per_ang | 0.03 | 0.03 | ✅ |
| spinpol | null | None | ✅ |
| maxiter | 500 | 500 | ✅ |
| gap_interp_scale | 0.5 | 0.5 | ✅ |
| dos_interp_scale | 1.0 | 1.0 | ✅ |
| k_max_boost | 2.0 | 2.0 | ✅ |
| fermi_smearing_metal | 0.02 | 0.02 | ✅ |
| fermi_smearing_semiconductor | 0.05 | 0.05 | ✅ |
| supercell_min_length_base | 10.0 | 10.0 | ✅ |
| supercell_min_length_boost | 5.0 | 5.0 | ✅ |
| relax_fmax | 0.01 | 0.01 | ✅ |
| relax_steps | 200 | 200 | ✅ |
| optimizer | FIRE | FIRE | ✅ |
| fix_cell | ab | ab | ✅ |
| symmetry_tol | 0.01 | 0.01 | ✅ |
| always_spinpol | false | False | ✅ |
| fm_nm_degenerate_tol_eV | 0.001 | 0.001 | ✅ |
| fm_nm_compare_before_m2 | true | True | ✅ |
| zero_step_verify | true | True | ✅ |
| zero_step_displacement | 0.05 | 0.05 | ✅ |
| zero_step_verify_threshold | 0.05 | 0.05 | ✅ |
| elastic_delta | 0.005 | 0.005 | ✅ |
| elastic_fmax | 0.01 | 0.01 | ✅ |
| elastic_relax_steps | 100 | 100 | ✅ |
| born_noise_sigma | 3.0 | 3.0 | ✅ |
| symmetry_noise_sigma | 3.0 | 3.0 | ✅ |
| phonon_supercell | [3, 3, 1] | [3, 3, 1] | ✅ |
| phonon_displacement | 0.01 | 0.01 | ✅ |
| phonon_displacement_convergence_test | false | False | ✅ |
| phonon_noise_sigma | 3.0 | 3.0 | ✅ |
| phonon_noise_floor_max_THz | 1.0 | 1.0 | ✅ |
| phonon_boundary_tighten_factor | 5.0 | 5.0 | ✅ |
| phonon_gamma_tol | -0.1 | -0.1 | ✅ |
| phonon_boundary_tol | -0.1 | -0.1 | ✅ |
| phonon_npoints_per_segment | 51 | 51 | ✅ |
| phonon_za_tol | -0.2 | -0.2 | ✅ |
| phonon_za_sigma_factor | 5.0 | 5.0 | ✅ |
| phonon_optical_tol | -0.05 | -0.05 | ✅ |
| small_lattice_elements | [C,B,N,O] | ['C','B','N','O'] | ✅ |
| small_lattice_min_length_multiplier | 2.0 | 2.0 | ✅ |
| small_lattice_min_length | 15.0 | 15.0 | ✅ |
| small_lattice_max_supercell | [7, 7, 1] | [7, 7, 1] | ✅ |
| ehull_threshold | 0.2 | 0.2 | ✅ |
| ehull_ref_pool_size | 3 | 3 | ✅ |
| use_local_ref | true | True | ✅ |
| skip_gap_probe | false | False | ✅ |
| auto_cores | true | True | ✅ |
| max_cores | 32 | 32 | ✅ |
| mpi | true | True | ✅ |
| scf_retry_max | 2 | 2 | ✅ |
| scf_retry_perturbs | [0.05, 0.1] | [0.05, 0.1] | ✅ |
| save_poscar | true | True | ✅ |
| save_phonon_pdf | true | True | ✅ |
| verbose | true | True | ✅ |
| relax_2d_mask | [true,true,false,false,false,true] | [T,T,F,F,F,T] | ✅ |

## MPI Status

Multi-rank GPAW execution requires an MPI runtime compatible with the GPAW/_gpaw build. Multi-rank behavior should be validated in the target HPC environment.

**Note:** Historical single-rank GPAW execution has been verified. Multi-rank execution behavior has NOT been independently demonstrated in this cleanup phase.

## Conclusion

All GPAW scientific parameters are verified consistent. No changes required.
