# DFCA Examples

This directory contains example scripts for understanding and using the DFCA package.

---

## CPU Quick Start

**File:** `cpu_quickstart.py`

A minimal CPU demonstration that:
1. Loads a 2D crystal structure from CIF
2. Converts it to DFCA representation format
3. Constructs the CrystalDiT model
4. Runs a forward pass (software smoke test)

**Run:**
```bash
PYTHONPATH=. python examples/cpu_quickstart.py
```

**Requirements:**
- pymatgen (for CIF parsing)
- torch

**What this demonstrates:**
- Crystal representation format (element encoding, lattice normalization)
- Model interface and parameter count
- Data → representation → model pipeline

**What this is NOT:**
- A scientific evaluation
- A generation quality test
- A performance benchmark

---

## Example Structure

**File:** `data/example_2d_crystal.cif`

| Property | Value |
|----------|-------|
| Formula | BN (hexagonal boron nitride) |
| Atoms | 2 (B, N) |
| Source | C2DB dataset (sample 2dm-4991) |

The CIF file is used only for API demonstration. See `data/README.md` for provenance details.

---

## Next Steps

For full usage, see:
- [docs/training.md](../docs/training.md) — Training a new model
- [docs/generation.md](../docs/generation.md) — Generating crystals (requires GPU)
- [docs/screening.md](../docs/screening.md) — Stability screening
- [docs/configuration.md](../docs/configuration.md) — Configuration options

---

## License Note

The example CIF file (`data/example_2d_crystal.cif`) is from the C2DB dataset.
Verify redistribution permissions before using in public repositories.
