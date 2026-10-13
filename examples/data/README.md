# Example Crystal Data

This directory contains example crystal structures for the DFCA CPU Quick Start.

---

## Example Structure: BN (Boron Nitride)

```
Example structure:     BN (hexagonal boron nitride)
Original dataset:      C2DB (Computational 2D Materials Database)
Original sample ID:    2dm-4991
Formula:               BN
Number of atoms:       2
Purpose:               API demonstration for crystal representation
```

### Structure Details

| Property | Value |
|----------|-------|
| Formula | BN |
| Space group | P1 |
| Lattice a | 2.509 Å |
| Lattice b | 2.509 Å |
| Lattice c | 20.0 Å (with vacuum) |
| Angle γ | 120° (hexagonal) |
| Atoms | B, N |

### Why This Structure?

- **Small**: Only 2 atoms, ideal for CPU demonstration
- **Common elements**: B and N are in DFCA element vocabulary
- **Representative**: Classic 2D material (hexagonal BN)
- **Valid**: Successfully parsed by pymatgen and DFCA representation

### Data Redistribution Status

**STATUS: UNKNOWN**

The source CSV file (`train.csv`) does not contain an explicit license file.
The structures appear to be from the C2DB database.

**If you plan to redistribute this CIF file:**
- Verify the license terms from the original C2DB source
- If redistribution is not permitted, remove this file and generate
  your own example structure instead

For the CPU Quick Start purpose, this file is used only to demonstrate
the DFCA preprocessing and representation pipeline.

---

## Generation

To generate this CIF from the dataset:

```python
import pandas as pd
df = pd.read_csv('Data/train.csv')
bn = df[df['material_id'] == '2dm-4991']
print(bn['cif'].values[0])
```
