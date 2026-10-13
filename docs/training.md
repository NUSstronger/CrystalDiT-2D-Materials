# Training

This document describes the DFCA training pipeline for the CrystalDiT model.

## Overview

Training uses a DDPM-based diffusion process with anisotropy-aware physical constraints:

1. **Forward diffusion:** Apply anisotropic noise to crystal tensors
2. **Model prediction:** CrystalDiT predicts clean x₀ from noisy input
3. **Loss computation:** MSE + physics-based constraint losses
4. **Optimization:** AdamW with timestep-dependent weighting

## Configuration

Training is configured via YAML files:

```bash
PYTHONPATH=. python scripts/train.py \
    --config configs/train.yaml \
    --data_dir ./Data \
    --output_dir ./output
```

Key configuration options:
- `--config`: Path to YAML configuration file
- `--data_dir`: Directory containing train.csv, val.csv
- `--output_dir`: Directory for checkpoints and logs
- `--seed`: Random seed for reproducibility

## Data Format

Training data is provided as CSV with CIF content:

```csv
id,prototype,formula,lattice_a,lattice_b,lattice_c,alpha,beta,gamma,structure
2dm-4991,BN,hBN,2.509,2.509,15.0,90.0,90.0,120.0,"data_2dm-4991 ..."
```

The `structure` column contains the full CIF content parsed by pymatgen.

**Reference:** [`dfca/data/dataset.py`](dfca/data/dataset.py)

## Loss Function

The training loss combines multiple components:

### Diffusion Loss

Standard MSE between predicted and target x₀:

```python
loss_diffusion = MSE(predicted_x0, target_x0)
```

### Physical Constraint Losses

Physics-based regularization to ensure physically plausible structures:

| Constraint | Purpose | Weight Decay |
|------------|---------|--------------|
| Atom validity | Valid elements | 30% → 70% |
| Lattice geometry | Valid unit cell | 30% → 70% |
| Slab centering | Centered in cell | 30% → 70% |
| Density | Physical density | 30% → 70% |
| Vacuum thickness | Minimum vacuum | 30% → 70% |

**Decay boundaries:** Constraint weight decreases from 1.0 to 0.0 over two ranges:
- 0% → 30%: Full constraint weight
- 30% → 70%: Linear decay
- 70% → 100%: No constraint weight

This ensures constraints guide early training but don't interfere with fine-tuning.

**Reference:** [`dfca/training/constraints.py:compute_physical_constraints`](dfca/training/constraints.py)

### Anisotropic Loss Weighting

Different weights for XY vs Z components:

```python
ATOM_XY_FEATURE_WEIGHTS = [1.5, 2.0, 1.0, 1.0]  # XY features
ATOM_Z_LOSS_WEIGHT = 0.1                         # Z weight (reduced)
ATOM_TOTAL_LOSS_COMBINE_WEIGHT = 15.9768         # Combination factor
```

This reflects that:
- XY features (element, x, y) are more important for chemical correctness
- Z features need gentler treatment due to variable vacuum thickness

## Anisotropic Noise Scaling

Forward diffusion uses different noise levels for XY vs Z:

```python
z_noise_scale = 0.113001          # Smaller noise for Z
lattice_c_noise_scale = 0.340659  # Larger noise for lattice c
```

This accounts for the fact that Z coordinates have different scale and variability than XY.

**Reference:** [`dfca/diffusion/gaussian.py:q_sample`](dfca/diffusion/gaussian.py)

## Optimization

Default optimizer settings:

- **Optimizer:** AdamW
- **Learning rate:** Configurable via YAML
- **Batch size:** Configurable via YAML
- **Epochs:** Configurable via YAML
- **Mixed precision:** Optional (config-dependent)

## Reproducibility

Set random seed for reproducibility:

```bash
python scripts/train.py --config configs/train.yaml --seed 42
```

See [`docs/randomness_and_reproducibility.md`](randomness_and_reproducibility.md) for detailed seed management.

## Hardware Requirements

- **GPU:** CUDA-capable GPU with ≥8GB VRAM recommended
- **Memory:** ~16GB RAM for typical batch sizes
- **Storage:** ~50GB for dataset and checkpoints

## Monitoring

Training progress is logged:
- Loss components (diffusion, constraints)
- Learning rate
- Gradient norms
- Validation metrics (if configured)

## Checkpointing

Checkpoints are saved to `--output_dir`:
- Model weights
- Optimizer state
- Training step
- Configuration snapshot

---

*Last updated: 2026-10-01*
