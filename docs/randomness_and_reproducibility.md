# Randomness and Reproducibility Documentation

Generated: 2026-10-01
Purpose: Stage 8 - Configuration & Environment Reproducibility

## Overview

This document describes how randomness is handled throughout the DFCA pipeline and
how to achieve reproducible results across training, generation, and screening stages.

---

## Randomness Sources

### Training Stage

| Source | RNG Type | Seed Mechanism | Notes |
|--------|----------|---------------|-------|
| PyTorch | `torch.manual_seed()` | Global seed | Sets CPU and GPU RNG |
| NumPy | `np.random.seed()` | Global seed | For data preprocessing |
| Python | `random.seed()` | Global seed | For hash randomization |
| DataLoader | Worker RNG | `generator` arg | Per-worker seed generation |
| CUDA | `cudnn.deterministic` | Global seed | Enables deterministic convolutions |
| CUDA | `cudnn.benchmark=False` | N/A | Disables auto-tuning |

**Critical Code Location**: `dfca/training/trainer.py:set_seed()`

```python
def set_seed(seed: int):
    """Set all RNG sources for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

### Generation Stage

| Source | RNG Type | Control Method |
|--------|----------|----------------|
| Diffusion sampling | `torch.manual_seed()` | `--seed` argument |
| Top-k decoder | `random.Random()` | `--topk_seed` argument |
| Batch ordering | Non-deterministic | No control (acceptable) |

### ML Screening Stage

| Source | Determinism | Notes |
|--------|------------|-------|
| MACE relaxation | Deterministic | Fixed model weights |
| FIRE optimizer | Deterministic | Same starting structure |
| Deduplication | Floating-point | `STRUCTURE_SIMILARITY_TOLERANCE=0.02` |

### DFT Validation Stage

| Source | Determinism | Notes |
|--------|------------|-------|
| GPAW SCF | Deterministic | With fixed k-point mesh |
| Phonopy | Deterministic | With fixed displacement |
| Structure relaxation | Deterministic | Converged to fmax |

---

## Reproducibility Checklist

### Training Reproducibility

```bash
# Record these for reproducibility:
PYTHONPATH=. python scripts/train.py \
    --seed 42 \
    --data_dir ./Data \
    --output_dir ./output \
    --epochs 100

# Check config was saved:
cat output/config.json | grep -E '"seed"|"learning_rate"|"batch_size"'
```

**Required to Record**:
- [ ] Random seed
- [ ] Data directory path
- [ ] Model architecture (hidden_size, depth, num_heads)
- [ ] Diffusion parameters (z_noise_scale, lattice_c_noise_scale)
- [ ] Learning rate and weight decay
- [ ] Checkpoint path

### Generation Reproducibility

```bash
# Reproducible generation command:
PYTHONPATH=. python scripts/generate.py \
    --checkpoint ./output/best_checkpoint.pt \
    --seed 42 \
    --topk_seed 20260504 \
    --num_samples 100 \
    --output_dir ./generated

# Verify noise scales match training:
PYTHONPATH=. python -c "
import torch
ckpt = torch.load('./output/best_checkpoint.pt', map_location='cpu')
print('z_noise_scale:', ckpt.get('args', {}).get('z_noise_scale'))
print('lattice_c_noise_scale:', ckpt.get('args', {}).get('lattice_c_noise_scale'))
"
```

**Required to Record**:
- [ ] Model checkpoint path
- [ ] Random seed (diffusion sampling)
- [ ] Top-k seed (if using top-k decoder)
- [ ] Diffusion steps
- [ ] Number of samples

### Screening Reproducibility

```bash
# Screening with fixed config:
PYTHONPATH=. python -c "
from dfca.screening import ScreeningPipeline, ScreeningConfig

cfg = ScreeningConfig(
    input_dir='./generated',
    output_dir='./screening',
    relax_fmax=0.05,  # MACE relaxation
    elastic_delta=0.005,
)
pipeline = ScreeningPipeline(cfg)
pipeline.run()
"

# Record screening config:
cp dfca/screening/config.py screening_config_backup.py
```

**Required to Record**:
- [ ] MACE model version
- [ ] All ScreeningConfig parameters
- [ ] Input directory
- [ ] Pass/fail thresholds

### DFT Reproducibility

```bash
# Record DFT environment:
gpaw --version > dft_environment.txt
python --version >> dft_environment.txt
pip freeze | grep -E 'gpaw|ase|phonopy' >> dft_environment.txt

# Run DFT validation:
PYTHONPATH=. python -m dfca.validation.cli \
    --input_dir ./screening/relaxed_cifs \
    --output_dir ./dft_validation
```

**Required to Record**:
- [ ] GPAW version
- [ ] All GPAWConfig parameters
- [ ] K-point meshes (auto-calculated)
- [ ] Convergence thresholds

---

## Environment Reproducibility

### Conda Environment Export

```bash
# Save complete environment
conda env export > environment.yml

# Create from saved environment
conda env create -f environment.yml
```

### Python Package Versions

```bash
# ML dependencies
pip freeze | grep -E 'torch|numpy|pymatgen|scipy|pandas' > ml_requirements.txt

# DFT dependencies
pip freeze | grep -E 'gpaw|ase|phonopy|mpi4py' > dft_requirements.txt

# All dependencies
pip freeze > all_requirements.txt
```

---

## Known Non-Deterministic Operations

### Training (Mitigated)

| Operation | Impact | Mitigation |
|-----------|--------|------------|
| CUDA convolution | Low | `cudnn.deterministic=True` |
| Distributed training | Medium | Single-GPU recommended for exact reproducibility |
| Multi-GPU batch ordering | Low | Different GPU counts produce identical models |

### Generation (Mitigated)

| Operation | Impact | Mitigation |
|-----------|--------|------------|
| Batch ordering | Low | Not scientifically significant |
| Multi-GPU sampling | Medium | Use `--seed` for diffusion noise reproducibility |

### ML Screening

| Operation | Impact | Notes |
|-----------|--------|-------|
| MACE relaxation | None | Deterministic with fixed weights |
| Deduplication | Low | Ewald sum tolerance = 0.02 |

### DFT

| Operation | Impact | Notes |
|-----------|--------|-------|
| SCF convergence | Low | Always converges to same minimum |
| K-point generation | Deterministic | Based on lattice parameters |

---

## Version Control Requirements

### Git

```bash
# Save exact commit
git log -1 --format="%H %s" > version.txt
git rev-parse HEAD > commit_hash.txt
```

### Data Versions

```bash
# Record dataset version
ls -la Data/ > data_manifest.txt
md5sum Data/*/*.cif > data_checksums.txt 2>/dev/null || true
```

### Model Checkpoints

```
# Checkpoint naming convention
output/
├── config.json          # Full training config
├── best_checkpoint.pt   # Best model (EMA)
├── last_checkpoint.pt   # Most recent
└── training.log        # Training progress
```

---

## Testing Reproducibility

### Quick Verification

```bash
# Test 1: Training seed produces same initial loss
PYTHONPATH=. python scripts/train.py --seed 42 --epochs 1 --output_dir /tmp/test1
PYTHONPATH=. python scripts/train.py --seed 42 --epochs 1 --output_dir /tmp/test2
diff /tmp/test1/training.log /tmp/test2/training.log

# Test 2: Same checkpoint produces same structures
PYTHONPATH=. python scripts/generate.py --checkpoint output/best_checkpoint.pt \
    --seed 42 --num_samples 10 --output_dir /tmp/gen1
PYTHONPATH=. python scripts/generate.py --checkpoint output/best_checkpoint.pt \
    --seed 42 --num_samples 10 --output_dir /tmp/gen2
diff <(ls /tmp/gen1/*.cif | sort) <(ls /tmp/gen2/*.cif | sort)
```

---

## Citation for Reproducibility

When citing this work for reproducibility, include:

```
DFCA version: <git commit hash>
Training seed: <seed>
Generation seed: <seed>
Diffusion steps: 1000
Noise scales: z=0.113001, lattice_c=0.340659
ML screening config: see configs/screening.yaml
DFT parameters: see configs/dft_validation.yaml
```

---

*Generated during Stage 8 Configuration & Environment Reproducibility*
