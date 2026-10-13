# DFCA Scientific Code Freeze

The DFCA scientific source code has completed:

- modularization;
- original-to-release completeness audit;
- scientific regression testing;
- configuration consistency verification;
- final release consistency checks.

**Scientific source code is frozen at this revision.**

Any subsequent modification to scientific implementation or experiment configuration requires corresponding regression revalidation.

---

## Frozen Scope

The scientific freeze covers:

- `dfca/` — Core scientific implementations
- `diffusion/` — Third-party diffusion infrastructure
- `configs/` — Scientific configuration parameters

## Non-Frozen Items

The following may be modified without scientific regression:

- README/documentation formatting and typos
- Citation metadata
- External artifact URLs and DOIs
- LICENSE file (when finalized by authors)
- Packaging metadata (pyproject.toml)
- Release hygiene artifacts

## Blocking Items for Public Release

1. **DFCA LICENSE** — Authors must finalize licensing terms
2. **MACE LICENSE** — Software and model license verification required
3. **Pretrained Checkpoint** — Must be archived with SHA256 checksum
4. **DFT/Phonon Artifacts** — Paper-relevant results pending HPC retrieval

## Scientific Regression Testing

Any modification to frozen scientific code must be validated against:

1. Unit tests (`pytest tests/unit/`)
2. Regression tests (`pytest tests/regression/`)
3. Configuration consistency (screening.yaml ↔ ScreeningConfig, dft_validation.yaml ↔ GPAWConfig)

---

*Freeze date: 2026-10-02*
