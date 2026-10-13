# Screening Pipeline

Generated crystal structures pass through a multi-stage screening pipeline to identify promising candidates for DFT validation.

## Paper-to-Implementation Stage Mapping

The paper describes a simplified scientific screening workflow that maps to implementation stages as follows:

| Paper Stage | Implementation Stage(s) | Purpose | Calculator/Method |
|-------------|------------------------|---------|-------------------|
| Composition Filter | S0 | Remove invalid elemental compositions | Element whitelist/blacklist |
| Geometry Check | S1 | Validate vacuum thickness, slab geometry | pymatgen Structure analysis |
| Symmetry Check | S2 | Verify layer group symmetry | spglib symmetry detection |
| Deduplication | S3 | Remove near-duplicate structures | StructureMatcher (RMSD) |
| ML Relaxation | S3.5 | Find local energy minimum | **MACE-MP-0** (sole MLIP) |
| Dimensionality Check | S-dim | Verify 2D connectivity | get_dimensionality_larsen |
| Thermodynamic Stability | S3T | E_above_hull calculation | pymatgen PhaseDiagram |
| Elastic Matrix | S4 | Mechanical stability criteria | Finite-difference + MACE |
| Phonon Stability | S5 | Dynamic stability (no imaginary freq) | phonopy + MACE forces |
| MD Stability | S7a, S7b | Thermal stability | NPT MD simulation |
| Convex Hull | S5' | Final thermodynamic verification | Materials Project API |

**Note:** Implementation stages (S0, S1, S2, S3, S3.5, etc.) are working-level identifiers.
The paper may aggregate these into simpler scientific categories. This mapping is provided
for reproducibility purposes.

## Pipeline Overview

```
Generated CIFs
      ↓
S0: Composition filter
      ↓
S1: Geometry check
      ↓
S2: Symmetry check
      ↓
S3: Deduplication
      ↓
S3.5: ML relaxation (MACE-MP-0)
      ↓
S5: Phonon stability
      ↓
Thermodynamic: E_above_hull
      ↓
DFT Validation Candidates
```

## Stage S0: Composition Filter

Filters structures by elemental composition:

- **Allowed elements:** Configurable whitelist
- **Forbidden elements:** Configurable blacklist
- **Stoichiometry:** Optional chemical formula constraints

**Rationale:** Remove structures with elements outside the target chemical space early in the pipeline.

**Reference:** [`dfca/screening/stages/s0_composition.py`](dfca/screening/stages/s0_composition.py)

## Stage S1: Geometry Check

Validates basic geometric properties:

| Check | Threshold | Rationale |
|-------|-----------|-----------|
| Vacuum thickness | ≥15 Å | Ensure non-interacting slabs |
| Slab thickness | Configurable | Avoid unrealistically thin/thick |
| Bond distances | Element-specific | Detect overlapping atoms |
| Cell angles | Near 90°/120° | Typical 2D lattice values |

**Reference:** [`dfca/screening/stages/s1_geometry.py`](dfca/screening/stages/s1_geometry.py)

## Stage S2: Symmetry Check

Validates layer group symmetry:

- **Layer group determination:** Uses spglib
- **Valid groups:** Configurable list (default: all 2D layer groups)
- **Centrosymmetry:** Optional check for polar structures

**Rationale:** Ensure structure has valid 2D crystallographic symmetry.

**Reference:** [`dfca/screening/stages/s2_symmetry.py`](dfca/screening/stages/s2_symmetry.py)

## Stage S3: Deduplication

Removes duplicate structures:

- **Similarity metric:** Based on atomic positions and cell parameters
- **Threshold:** Configurable RMSD cutoff (default: 0.1 Å)
- **Method:** Hierarchical clustering with single linkage

**Rationale:** Avoid redundant calculations on essentially identical structures.

**Reference:** [`dfca/screening/stages/s3_dedup.py`](dfca/screening/stages/s3_dedup.py)

## Stage S3.5: ML Relaxation

Relaxes structures using MACE-MP-0 ML potential:

- **Purpose:** Find local energy minimum
- **Method:** MACE-MP-0 from mace-offential package
- **Convergence:** Configurable force/energy thresholds

**Outputs:**
- Relaxed structure (CIF)
- Energy per atom
- Forces on atoms

**Rationale:** ML relaxation is fast and provides approximate energetics before expensive DFT.

**Reference:** [`dfca/screening/stages/s3_5_ml_relax.py`](dfca/screening/stages/s3_5_ml_relax.py)

### ML Relaxation Stability Classification

After ML relaxation, structures are classified by stability:

| Stability | Condition | Action |
|-----------|-----------|--------|
| HIGH | E_form < -1.0 eV/atom | Proceed to S5 |
| MEDIUM | -1.0 ≤ E_form < 0.0 eV/atom | Proceed to S5 |
| LOW | E_form ≥ 0.0 eV/atom | Filter out |

**Reference:** [`dfca/screening/stages/s3_5_ml_relax.py`](dfca/screening/stages/s3_5_ml_relax.py)

## Stage S5: Phonon Stability

Validates dynamic stability via phonon calculations:

- **Method:** phonopy with MACE-computed forces
- **Stability criterion:** No imaginary frequencies at Γ point
- **Supercell:** Configurable size (default: 3×3×1)

**Rationale:** Dynamically unstable structures (imaginary frequencies) will spontaneously distort.

**Reference:** [`dfca/screening/stages/s5_phonon.py`](dfca/screening/stages/s5_phonon.py)

## Thermodynamic Screening: E_above_hull

Calculates thermodynamic stability:

- **Method:** Compare against convex hull from C2DB/Materials Project
- **Stability criterion:** E_above_hull < 0.1 eV/atom (configurable)
- **Database:** C2DB hull data

**Rationale:** Structures far from the convex hull are thermodynamically unfavorable.

**Reference:** [`dfca/screening/stages/s_thermo.py`](dfca/screening/stages/s_thermo.py)

## Pipeline Configuration

All stages are configured via [`configs/screening.yaml`](configs/screening.yaml):

```yaml
stages:
  s0_composition:
    allowed_elements: [H, B, C, N, O, F, Si, P, S, Cl, Br]
    forbidden_elements: [Li, Na, K, Rb, Cs, Fr]
  
  s1_geometry:
    min_vacuum: 15.0  # Å
    min_bond_distance: 1.0  # Å
  
  s3_5_ml_relax:
    mace_model: MACE-MP-0
    convergence: tight
  
  s5_phonon:
    supercell: [3, 3, 1]
    min_freq_thz: 0.0
```

## Running the Pipeline

```bash
PYTHONPATH=. python -m dfca.screening.pipeline \
    --input ./candidates \
    --output ./screened \
    --config configs/screening.yaml
```

## Output

Each stage produces:
- Passed structures (CIF)
- Filtered structures with reason
- Summary statistics

Final output includes:
- Screened candidates for DFT validation
- Stability metrics
- Phonon properties

---

*Last updated: 2026-10-01*
