# Pretrained Model Checkpoint

## Status

**PENDING** — Checkpoint not yet available in public release.

## For Reproduction

To generate 2D crystal structures with DFCA, a trained checkpoint is required.

### Obtaining the Checkpoint

The official DFCA checkpoint will be released with the manuscript.

If you need the checkpoint for reproducibility purposes:

1. Check the GitHub releases page for the latest checkpoint release
2. Or contact the authors for checkpoint access

### Checkpoint Information (When Available)

| Field | Value |
|-------|-------|
| Model architecture | CrystalDiT |
| Hidden size | 512 |
| Number of heads | 8 |
| Depth | 18 |
| Training data | C2DB 2D materials |
| Checkpoint file | `dfca_best.pt` |
| File size | ~500 MB |
| SHA256 | TODO |

### Placeholder

```bash
# Download checkpoint (when available)
# wget https://github.com/USER/DFCA/releases/download/v1.0.0/dfca_best.pt

# Or use placeholder for testing
python scripts/generate.py \
    --config configs/generate.yaml \
    --checkpoint checkpoints/dfca_best.pt \
    --output_dir ./candidates \
    --num_samples 10
```

---

*Checkpoint will be uploaded upon manuscript acceptance or upon request.*
