# RFT-QPU-Sierpinski — level-1 physical demonstrator model

**Package:** v0.3 research update · **Evidence status:** executable numerical prototype and candidate phase-coherent hardware mapping. No chip has been fabricated or measured.

This package contains the reproducible finite-graph SU(2) model, projected logical controls, a proposed 12-transmon level-1 mapping, the first two-cell projected-entangler calculation, design tables, test suite and engineering gate documents.

## Engineering prototype

The numerical and engineering package is maintained in [engineering/physical_prototype](engineering/physical_prototype/README.md). Its level-1 mapping contains six graph sites, nine graph edges and 22 nonzero effective exchange channels.

The merged main baseline includes the level-1 prototype and website architecture update. The new qutrit/Floquet screening changes described below are local development results pending PR validation. Numerical values are model outputs, not measurements.

| Quantity | Numerical result |
|---|---:|
| Level-1 modeled modes / proposed transmon mapping | 12 |
| Ground-doublet splitting divided by J | 1.61 × 10^-15 |
| Gap to the next level divided by J | 1.3937126931 |
| Best local projected-control coefficient | 0.1770433 |
| Two-cell modeled modes | 24 |
| Projected interaction coefficient divided by χ | 0.00783608327 |
| Idealized gate time at assumed χ/(2π) = 10 MHz | 6.38074 μs |

The near-zero doublet splitting is a floating-point result, not a formal proof of exact degeneracy. The two-cell gate time is an idealized projected-model estimate, not a measured gate.

## Complex-Z and nine-tone engineering status

The isolated Z edge has a 245 MHz phase-coherent parametric candidate with conjugate phases +135°/−135°. The reduced four-qutrit block gives one-excitation process overlap 0.999609 and two-excitation leakage stress of 1.17×10^-5 under its stated effective-drive assumptions.

**The complete nine-tone schedule is not cleared for simultaneous operation.** The new first-order collision audit finds zero primary resonance margin and 73 primary pump/sideband warnings within 10 MHz across the 22 channel rows. Conditional second/third harmonics and pairwise intermodulation products raise the warning count to 653. These are possible resonances if cross-coupling exists; they are not measured error probabilities.

Run the screen from the package directory:

```bash
PYTHONPATH=src python scripts/run_floquet_audit.py
```

See [the collision audit](engineering/physical_prototype/docs/FLOQUET_COLLISION_AUDIT.md). The audit is a deterministic first-order screen, not a full multi-frequency Floquet/Sambe simulation.

## Remaining physical gates

1. Redesign the six local rotating-frame offsets and re-run the collision screen with a declared guard band.
2. Measure or extract the complex 22×22 pump-channel transfer matrix.
3. Build an explicit data–coupler–data circuit model with extracted capacitance/Josephson parameters.
4. Run full multitone Floquet, residual-ZZ, spectator, leakage, EM and open-system validation.
5. Fabricate and measure a one-cell demonstrator before making hardware performance claims.

The current coefficient CSV is not a foundry-ready netlist. The package is not a fabricated or fault-tolerant quantum computer.

## Repository map

- `engineering/physical_prototype/` — numerical model, hardware coefficient export and validation.
- `docs/ARCHITECTURE.md` — mathematical-to-transmon architecture.
- `docs/VALIDATION_PLAN.md` — validation gates.
- `docs/DISCLOSURE_BOUNDARY.md` — established versus proposed claims.
- `docs/index.html` — architecture presentation.

The RFT-QPU SU(2) model must not be conflated with the distinct signed-Z2 operator family in Phi-Genesis.
