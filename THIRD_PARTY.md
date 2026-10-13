# Third-Party Code Acknowledgments

DFCA builds upon several third-party implementations. This document provides detailed attribution for all third-party code used in the project.

## Diffusion Infrastructure

### GaussianDiffusion Base Class

The `diffusion/gaussian_diffusion.py` module is based on OpenAI's diffusion implementations:

- **ADM (Assisted Diffusion Model):** https://github.com/openai/guided-diffusion
- **IDDPM (Improved Denoising Diffusion Probabilistic Models):** https://github.com/openai/improved-diffusion
- **GLIDE:** https://github.com/openai/glide-text2im

**DFCA modifications:** Extended the base `GaussianDiffusion` class with crystal-specific functionality including:
- Separate noise scaling for Z coordinates (`z_noise_scale = 0.113001`)
- Anisotropic lattice handling (`lattice_c_noise_scale = 0.340659`)
- Crystal-specific loss weighting (`ATOM_XY_FEATURE_WEIGHTS`, `ATOM_Z_LOSS_WEIGHT`)

### DiT Architecture Components

The `diffusion/model.py` module implements transformer components adapted from the DiT (Diffusion Transformer) architecture:

- **DiTBlock:** Transformer block with adaptive layer norm modulation
- **TimestepEmbedder:** Sinusoidal timestep embedding
- **modulate():** Adaptive layer norm modulation function

**Source:** Based on the DiT architecture from the paper "Scalable Diffusion Models with Transformers" (Peebles & Xie, 2023) and associated open-source implementations.

- **DiT Paper:** https://arxiv.org/abs/2212.09748
- **DiT Reference Implementation:** https://github.com/facebookresearch/DiT

**DFCA modifications:** Adapted for crystal structure generation with:
- Crystal-specific embedding layers (`CrystalEmbedder`)
- Separate handling for lattice and atom features
- Attention masking for variable atom counts

## Scientific Libraries

### pymatgen

**Purpose:** Crystal structure parsing and manipulation
**License:** MIT
**Citation:** Ong, S.P. et al. (2013). Python Materials Genomics (pymatgen)

Used for:
- CIF file parsing
- Lattice matrix extraction
- Structure validation

### MACE (Machine Learning Accurate CH Energy)

**Purpose:** ML interatomic potential for structure relaxation
**License:** MACE LICENSE VERIFICATION REQUIRED BEFORE PUBLIC RELEASE
**Citation:** Batatia, I. et al. (2022). A Foundation Model for Atomistic Materials Chemistry. arXiv:2211.15420

Used in:
- Screening stage S3.5 (ML relaxation)
- Screening stage S5 (phonon stability with MACE forces)

### GPAW

**Purpose:** First-principles DFT calculations
**License:** GPLv3
**Citation:** Larsen, A.H. et al. (2017). The atomic simulation environment—a review. J. Phys.: Condens. Matter, 37, 273201. (ASE)

GPAW-specific citation: Enkovaara, J. et al. (2010). Electronic structure calculations with GPAW: a real-space implementation of the projector augmented-wave method. J. Phys.: Condens. Matter, 22, 253202.

Used in:
- DFT validation module (`dfca/validation/`)
- Structure relaxation (M1)
- Elastic constants (M2)
- Phonon dispersion (M3)

### ASE (Atomic Simulation Environment)

**Purpose:** Atomistic simulation infrastructure
**License:** LGPLv3
**Citation:** Larsen, A.H. et al. (2017). The atomic simulation environment—a review. J. Phys.: Condens. Matter, 37, 273201.

Used as the Python interface for GPAW calculations.

### phonopy

**Purpose:** Phonon calculations
**Citation:** Togo, A. & Tanaka, I. (2015). First principles phonon calculations

Used in:
- Phonon stability screening (S5)
- DFT-level phonon dispersion (M3)

## Dataset

### C2DB (Computational 2D Materials Database)

**Purpose:** Training and validation data for 2D crystal structures
**License:** See C2DB website for terms
**Citation:** Haastrup, S. et al. (2018). The Computational 2D Materials Database

**Data redistribution:** Verify license terms before redistributing raw data.

## License Compatibility

All third-party code is used in accordance with their respective licenses:
- OpenAI repositories (ADM/IDDPM/GLIDE): MIT License
- DiT (Peebles & Xie): BSD License
- pymatgen: MIT License
- MACE: VERIFICATION REQUIRED BEFORE PUBLIC RELEASE
- GPAW: GPLv3
- phonopy: BSD License
- ASE: LGPLv3

DFCA code licensing terms are being finalized prior to public release.

---

*Last updated: 2026-10-01*
