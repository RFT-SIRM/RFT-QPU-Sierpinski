# RFT-QPU-Sierpinski — research and strategic-partner brief

**Project author attribution:** Evgeny Zaprudnov  
**Date:** 12 November 2026  
**Handling:** public non-confidential technical and collaboration brief.

## Investment thesis

RFT-QPU-Sierpinski explores a quantum-processing architecture in which the connectivity graph is an intentional mathematical structure. A self-similar Sierpiński-gasket graph carries non-commuting SU(2) edge transport. The first proposed superconducting embodiment maps a graph site to a pair of transmon modes and encodes a candidate logical degree of freedom in a two-dimensional low-energy subspace.

The proposition is not that a fault-tolerant quantum computer already exists. The proposition is that a specific graph-structured Hamiltonian, coefficient map and projected-control programme can be tested through a staged physical demonstrator.

## What exists today

**Numerical architecture**
- Finite Sierpiński graph and SU(2) Hamiltonian models for levels 1–5.
- Candidate low-energy doublet, leakage gap and projected-control calculations.
- Proposed level-1 map with 6 graph sites, 9 edges, 12 transmon modes and 22 effective exchange channels.
- Generated hardware coefficient and frequency tables.

**Circuit and gate work**
- Circuit-derived three-mode SQUID-coupler model and staged gate simulations.
- Stage 11B rebuild of the A–coupler–B product Hamiltonian in the re-quantized coupler basis.
- Initial 120/240/480 temporal convergence record and local pulse retune.
- Static two-cell projection for a candidate differential-density interaction.

**Software reproducibility**
- The merged Stage 11B engineering checkpoint passed GitHub Actions run #23 on its reviewed PR head.
- The public-release baseline commit db606c428183aab0b637ce449d08b604d260e0e4 passed [GitHub Actions run #29](https://github.com/RFT-SIRM/RFT-QPU-Sierpinski/actions/runs/43134406595): 78 tests and three reproducible calculation steps succeeded.
- The historical local pre-release record reports 75 passing tests.
- The original Stage 11B baseline JSON and matrix archive are tracked; the later local retune's raw JSON/NPZ outputs are not yet tracked.

## Selected numerical indicators — with their proper scope

| Indicator | Result | Evidence class |
|---|---:|---|
| Level-1 ideal leakage gap | 1.3937127 J | Finite graph Hamiltonian |
| Level-1 local projected-control scale | 0.1770433 | Ideal projected-control calculation |
| Stage 11B retuned five-level process overlap | 0.999999979376 | Closed-system three-mode model, local-Z fitted |
| Stage 11B retuned average logical-state fidelity including leakage | 0.999999980365 | Closed-system projected-matrix calculation |
| Stage 11B maximum sampled logical leakage | 3.312 × 10⁻⁴ | Sampled within the simulated pulse |
| Two-cell projected interaction | 0.00783608327 χ | Static tensor-product projection |
| Ideal two-cell time estimate | 6.38074 μs | Assumes χ/(2π) = 10 MHz |

The Stage 11B three-mode gate is not the full 12-mode level-1 graph device. The process-overlap figure is not randomized-benchmarking data, a measured physical gate fidelity or an independently qualified device result.

## Why a staged demonstrator is commercially relevant

The first milestone is a 12-transmon cell capable of implementing the intended graph Hamiltonian and reproducing the candidate spectrum and projected controls. The second milestone is a 24-transmon two-cell demonstrator with a measured entangling interaction. Only after these gates pass should the programme expand to modular processor tiles.

The scale counts are structural. A chain of 1, 2, 10, 100 and 1,000 level-1 cells corresponds to 12, 24, 120, 1,200 and 12,000 data transmons, respectively, before coupler/control/readout overhead. These counts are not a cost, yield or wiring forecast.

## Differentiation and comparison discipline

The architecture is not a new physical substrate competing with transmons: the first embodiment uses superconducting transmons. The research question is whether a graph-structured SU(2) Hamiltonian and its candidate logical subspace can provide a useful architecture and control abstraction.

No claim is made that the design outperforms IBM, Google, Quantinuum or any other platform. Its current numerical outputs cannot be directly compared with measured physical gate errors or logical error rates. The comparison document explains the relevant noise channels and the evidence gap.

## Principal risks a technical partner must help close

1. **Complex Z-link implementation:** the current resonant Z edge requires complex diagonal hopping phases; a single real static coupler is insufficient.
2. **Pump collisions:** the current graph-wide nine-tone screen reports 73 primary and 653 conditional warnings; simultaneous operation is not cleared.
3. **Thermal scale:** at the illustrative J/(2π) = 10 MHz, the level-1 gap is about 13.94 MHz, while kBT/h at 10 mK is about 208.37 MHz. Passive thermal protection is not established.
4. **Open-system performance:** T1/T2, thermal population, measured flux-line transfer, pump phase noise and crosstalk are not yet part of the gate model.
5. **Physical validation:** no chip has been fabricated, measured or independently reviewed.
6. **Retune reproducibility:** the raw local retune outputs must be archived before this result is treated as a fully reproducible repository checkpoint.

## Partner capabilities sought

A credible next-stage partner would contribute some combination of superconducting-circuit design, tunable-coupler engineering, cryogenic packaging, EM/layout extraction, phase-coherent microwave control, calibration, readout, fabrication, circuit-QED measurement and independent benchmarking.

## IP, licensing and collaboration

The repository is being prepared as a public technical record under Business Source License 1.1 (BUSL-1.1) accompanied by a separate, limited patent grant. The source licence permits non-production use under its terms; commercial production or manufacture requires a separate written agreement. The initial BUSL term is source-available, not OSI-approved open source. The Change Date is 12 November 2030, or the fourth anniversary of first public distribution of the relevant version if earlier; the Change License is GPL-2.0-only.

The supplemental patent grant is limited to patent claims the Licensor actually owns or lawfully controls and that are necessarily infringed by the Licensor's contributions. It does not create a patent or extend production rights beyond the source licence. No patent application number, filing date, office or grant is recorded in the repository; this is a repository-only observation. Public disclosure may affect patent novelty and filing options by jurisdiction. See [LICENSE](LICENSE), [PATENTS.md](PATENTS.md) and [IP_AND_LICENSING.md](IP_AND_LICENSING.md).

The project is open to technical review, research collaboration and discussions with groups capable of helping to resolve the circuit and experimental gates. No valuation, exclusivity, licence, funding commitment or partner agreement is implied by this brief.

This document is a factual summary of the present evidence, not an investment offer, securities solicitation, patentability opinion or representation of experimental performance.
