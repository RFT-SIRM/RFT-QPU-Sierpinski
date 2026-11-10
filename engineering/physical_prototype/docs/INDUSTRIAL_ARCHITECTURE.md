# From one qubit cell to a processor

## Architecture decision

Use a modular superconducting-transmon tile as the first hardware embodiment. Each tile is one SG level-1 cell: six graph sites, two transmons per site, and a single-excitation logical doublet. Connect tiles only after one tile's Hamiltonian, controls and leakage are experimentally characterized.

## Stage A — one logical cell

**12 data transmons.** Implement 9 graph edges / 22 effective exchange channels. The experiment is a one-logical-qubit proof of physical realization, not a computation platform yet.

Deliverables: chip, microwave/coupler netlist, phase calibration, spectrum, eigenstate reconstruction, projected-control matrices, reset/readout calibration, leakage and noise report. The resonant complex Z-link in the initial degree-frequency plan must first receive a concrete phase-engineered coupler solution.

## Stage B — two-cell entangling demonstrator

**24 data transmons.** Couple two independently calibrated level-1 cells at one selected anchor site per cell. The target interaction is a number-conserving spin-dependent cross-Kerr term

`H_AB/hbar = chi * S_z(A,v) * S_z(B,w)`,

where `S_z(v) = (n_v_up - n_v_dn)/2`.

At the logical level this becomes

`P_A P_B H_AB P_A P_B = (hbar chi/4) (c_A . sigma_A) tensor (c_B . sigma_B)`

for the calibrated local projection vectors. A practical circuit can synthesize the differential-density product from four pairwise cross-Kerr channels between the two modes at anchor A and the two modes at anchor B. This is a design target: the four coefficients, residual single-cell Stark shifts, excitation conservation and leakage must be derived and measured.

Acceptance at Stage B is a calibrated entangling gate with process tomography, leakage, crosstalk and repeatability measured. Until this succeeds the project has not demonstrated a universal quantum processor.

## Stage C — modular logical array

Replicate level-1 cells and connect only nearest-neighbour logical modules initially. Use modular microwave/control distribution, multiplexed readout and a calibrated inter-cell coupler layer. A 1D chain is the first engineering topology; 2D placement and fractal module-to-module connectivity are later decisions informed by routing and error data.

## Scale scenarios

The counts below are structural counts from the current Hamiltonian mapping, not manufacturing estimates. They exclude coupler control electronics, filtering, packaging, wiring, cryostat infrastructure and spare/test channels.

| Logical cells | Data transmons | Internal SG exchange channels | Intra-site spin-mixing links | Cross-cell ZZ terms for a nearest-neighbour chain |
|---:|---:|---:|---:|---:|
| 1 | 12 | 22 | 6 | 0 |
| 2 | 24 | 44 | 12 | 4 |
| 10 | 120 | 220 | 60 | 36 |
| 100 | 1,200 | 2,200 | 600 | 396 |
| 1,000 | 12,000 | 22,000 | 6,000 | 3,996 |

Each row assumes four cross-Kerr pair terms per nearest-neighbour cell link. The entangler topology is not yet experimentally established.

## Why the first prototype is level 1, not level 5

The QPU repository's referenced control scale `g_eff approximately 0.015085` is reproduced by the level-5 local projection. The full finite-level calculation in this package shows that increasing the SG refinement rapidly reduces the lowest leakage gap:

| SG level | Graph sites | Data transmons | Gap / J | Best local `g_eff` |
|---:|---:|---:|---:|---:|
| 1 | 6 | 12 | 1.393713 | 0.177043 |
| 2 | 15 | 30 | 0.397335 | 0.079709 |
| 3 | 42 | 84 | 0.088608 | 0.034749 |
| 4 | 123 | 246 | 0.015864 | 0.017990 |
| 5 | 366 | 732 | 0.002986 | 0.015085 |

Level 1 is selected because it is the smallest non-Abelian construction and has the largest leakage gap and local control factor among the tested levels. Level 5 is retained as a larger research reference, not as the first fabricated tile.

To preserve the same *absolute* gap while moving from level 1 to level 5, the coupling scale `J` would need to increase by about 467 times. That makes a direct level-5 transmon realization a materially different engineering challenge, not just a larger copy of the first chip.

## Industrial system layers

A processor programme will need, in addition to the quantum tile:

1. **Cryogenic package:** microwave launches, ground strategy, thermal anchoring, magnetic shielding, filtering and heat-load budget.
2. **Qubit/coupler layer:** transmon pairs, tunable couplers, pump ports, flux bias, readout resonators and isolation.
3. **Control layer:** phase-coherent pump generation, frequency planning, predistortion, calibration database and drift tracking.
4. **Readout layer:** multiplexed resonator drive, low-noise amplification, digitization, assignment calibration and leakage discrimination.
5. **Classical control:** deterministic pulse scheduler, graph-to-device compiler, pulse optimizer, calibration orchestration and fault/error logs.
6. **Logical layer:** encoded-state preparation, projected gate library, inter-cell entanglers, leakage-reduction and eventually error correction.
7. **Verification layer:** independent spectrum fitting, randomized/characterized gate benchmarking, tomography, noise spectroscopy and reproducibility records.

No industrial component counts should be frozen until Stage A identifies the dominant control/readout wiring and Stage B validates the inter-cell gate.

## Two-cell entangler calculation

The companion `results/two_cell_entangler_report.json` performs the tensor-product projection numerically. For the level-1 anchor vertex 5, `P S_z P` has eigenvalues `+/-0.0885216543`, giving

`H_L,AB / hbar = chi * 0.00783608327 * (n_A . sigma_A) tensor (n_B . sigma_B)`.

The projected interaction eigenvalues at `chi/J = 1` are `+/-0.00783608327` (each twice). This is a nonzero Ising-equivalent two-logical-qubit interaction; it is entangling after local basis rotations. A first physical realization of the differential-density term requires four cross-Kerr coefficients with sign pattern `(+,-,-,+)` between the two anchor-site mode pairs; their netlist is in `hardware/level1/dual_cell_entangler_channels.csv`.

With the illustrative assumption `chi/(2 pi) = 10 MHz`, the ideal projected maximally-entangling time is approximately **1.595 microseconds**. The full two-cell matrix (144 states in the product of the two one-excitation manifolds) was also diagonalized for `chi/J = 0.01, 0.05, 0.10`; the gap after the lowest logical quartet remains approximately `1.3934 J`, `1.3921 J`, and `1.3905 J`, respectively. These are static Hamiltonian calculations. They omit the switching envelope, open-system decoherence, coupler parasitics, pulse error and leakage during the gate; the gate is not experimentally validated.
