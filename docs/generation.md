# Generation

This document describes the DFCA crystal generation pipeline.

## Overview

Generation uses the trained CrystalDiT model to sample new 2D crystal structures from random noise:

1. **Initialization:** Start from Gaussian noise
2. **Denoising loop:** Iteratively apply model (1000 DDPM steps)
3. **Decoding:** Convert tensors to pymatgen Structure
4. **Export:** Save as CIF files for screening

## Configuration

Generation is configured via YAML files:

```bash
PYTHONPATH=. python scripts/generate.py \
    --config configs/generate.yaml \
    --checkpoint /path/to/checkpoint \
    --output_dir ./candidates \
    --num_samples 100 \
    --device cuda
```

Key configuration options:
- `--config`: Path to YAML configuration file
- `--checkpoint`: Path to trained model checkpoint
- `--output_dir`: Directory for generated CIF files
- `--num_samples`: Number of structures to generate
- `--device`: Device for inference (cuda/cpu)

## Sampling Process

### DDPM Sampling

The model follows the standard DDPM reverse process:

```python
for t in reversed(range(T)):
    # Model predicts x₀ from x_t
    predicted_x0 = model(x_t, t)
    # Denoise one step
    x_t = p_sample(predicted_x0, t)
```

Where T = 1000 timesteps.

### Anisotropic Handling

During sampling, anisotropic noise scaling is reversed:
- Z coordinates use smaller step sizes (matching training)
- Lattice c vector uses different scaling

## Output

Generated structures are saved as CIF files:

```
output_dir/
├── generated_000.cif
├── generated_001.cif
├── ...
└── metadata.json
```

The `metadata.json` contains generation parameters for reproducibility.

## Post-Generation

Generated CIFs should be processed through the screening pipeline before any scientific use:

```
Generated CIFs → S0 → S1 → S2 → S3 → S3.5 → S5 → Thermodynamic
```

See [`docs/screening.md`](screening.md) for screening documentation.

## Hardware Requirements

- **GPU:** CUDA-capable GPU with ≥8GB VRAM for efficient sampling
- **Memory:** ~8GB RAM
- **Time:** ~30 seconds per structure on GPU (depends on model size)

## Quality Considerations

Generated structures are **raw candidates**, not validated materials:

- May contain geometrically implausible atomic arrangements
- May violate physical constraints (vacuum thickness, density)
- Require screening before scientific interpretation

**Always run the full screening pipeline before analyzing results.**

## Batch Generation

For large-scale generation campaigns:

```bash
# Generate 1000 structures in batches of 100
for i in {0..9}; do
    PYTHONPATH=. python scripts/generate.py \
        --config configs/generate.yaml \
        --checkpoint checkpoint.pt \
        --output_dir ./batch_$i \
        --num_samples 100 \
        --device cuda
done
```

## Troubleshooting

### Out of Memory

Reduce batch size or switch to CPU:
```bash
--device cpu  # Slower but uses less memory
```

### Invalid Structures

Generated structures that fail to decode:
- Check generation parameters
- Verify checkpoint is valid
- May indicate model training issues

### Low Diversity

If generated structures are too similar:
- Check sampling temperature (if implemented)
- Verify training covered sufficient chemical space
- Consider retraining with different data

---

*Last updated: 2026-10-01*
