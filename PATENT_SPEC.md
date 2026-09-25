# RFT-QPU-Sierpinski — Patent-Oriented Technical Specification

**Technical disclosure for patent counsel review — not legal advice**

## 1. Title

**Quantum-processing architecture employing self-similar graph connectivity, non-Abelian SU(2) transport, and projected low-dimensional logical encoding**

## 2. Technical Field

The disclosure relates to quantum information processing, quantum hardware, graph-based Hamiltonians, non-Abelian gauge/connection structures, self-similar and fractal connectivity, logical subspace encoding, and control of quantum states through projected operators.

## 3. Background

Conventional quantum processors generally implement logical operations through physical qubits arranged in device-specific connectivity graphs. This disclosure investigates a different architecture in which the connectivity graph itself is a designed mathematical object and carries an internal SU(2)-valued transport structure.

The companion Evgeny's Theorem work provides the mathematical anchor for a gauge-invariant spectral-moment construction on Sierpiński-gasket graphs. The present disclosure extends that construction into a candidate logical-qubit architecture.

## 4. Summary of the Disclosure

In one embodiment, a quantum-processing element comprises:

1. a self-similar graph with vertices and edges;
2. a two-component internal Hilbert degree of freedom associated with graph vertices;
3. SU(2)-valued transport operators associated with selected edges;
4. a Hamiltonian formed from graph degree terms and transported edge hopping terms;
5. a selected two-dimensional low-energy subspace of the Hamiltonian;
6. logical control operators obtained by projection of physical/internal operators into that subspace.

A representative edge transport is

$$U_{ab}=\exp(-i\theta\sigma_\alpha/2).$$

A nominal configuration uses `θ = π/2` and cyclic selection of Pauli axes.

## 5. Mathematical Construction

Let `G=(V,E)` be a graph and let each vertex carry `C²`. Define

$$
H=D\otimes I_2-\sum_{(a,b)\in E}|a\rangle\langle b|\otimes U_{ab}+\mathrm{h.c.}
$$

where `D` is the graph degree operator and each `U_ab ∈ SU(2)`.

A logical projector `P` satisfies

$$P^2=P,\qquad \operatorname{Tr}(P)=2.$$

The logical operators are obtained by projection:

$$X_L=P S_xP,\qquad Y_L=P S_yP,\qquad Z_L=P S_zP.$$

The physical implementation is required to verify that these projected controls are sufficiently independent, calibrated, and spectrally isolated to support the intended gate set.

## 6. Spectral Anchor

The companion mathematical work reports the fourth spectral-moment defect

$$
\Delta_m(H^4,\theta)=-16(3^{m-1}+1)\sin^2(\theta/2).
$$

At `θ = π/2`, normalization by `3^(m+1)+3` yields the asymptotic invariant `−8/9`.

This invariant is a spectral-moment quantity. It is not asserted to be an energy gap.

## 7. Gauge Covariance

Under a local transformation `g_v ∈ SU(2)` at each vertex, edge transport transforms as

$$U_{ab}\mapsto g_aU_{ab}g_b^\dagger.$$

The corresponding block-diagonal unitary acts by conjugation on the Hamiltonian, preserving its spectrum. The software core contains a numerical covariance check for this transformation law.

Gauge covariance must not be conflated with immunity to non-gauge laboratory noise.

## 8. Candidate Logical-Qubit Embodiment

A candidate qubit is encoded into a selected two-dimensional low-energy subspace `Q = Ran(P)`. The selection procedure may use an energy window, symmetry criterion, or optimization criterion.

An implementation may include automated checks for:

- dimension of `Q`;
- minimum spectral separation from leakage states;
- matrix representation of projected controls;
- commutator structure;
- leakage under control pulses;
- sensitivity to parameter disorder.

## 9. Illustrative Claim Concepts

The following are **claim concepts for counsel review**, not final legal claims:

### Claim Concept A — Processing element
A quantum-processing element comprising a self-similar graph, an internal two-dimensional degree of freedom at graph vertices, SU(2)-valued edge transports, and a Hamiltonian coupling graph connectivity to said transports.

### Claim Concept B — Non-Abelian transport
The processing element of Concept A wherein transport axes are selected from multiple non-commuting generators of SU(2).

### Claim Concept C — Fractal geometry
The processing element wherein the graph is a recursively generated Sierpiński-gasket graph or an isomorphic self-similar graph family.

### Claim Concept D — Logical encoding
The processing element wherein a logical qubit is encoded in a selected two-dimensional low-energy eigenspace or invariant subspace of the Hamiltonian.

### Claim Concept E — Projected controls
The processing element wherein logical controls are obtained by projection of physical/internal operators into the selected two-dimensional subspace.

### Claim Concept F — Spectral certification
A method comprising computing one or more spectral moments of the processing element and using a normalized spectral-moment invariant as a certification observable for the architecture.

### Claim Concept G — Control and validation method
A method comprising selecting a two-dimensional subspace, computing projected controls, measuring leakage separation, and rejecting an implementation that fails predetermined spectral or control criteria.

## 10. Alternative Embodiments

Possible embodiments include superconducting circuits, flux-controlled couplers, semiconductor spin systems, trapped particles, photonic networks, synthetic quantum simulators, and other physical systems capable of implementing an effective SU(2)-valued transport Hamiltonian.

These embodiments are implementation hypotheses, not experimental results demonstrated by this repository.

## 11. Prior-Art Positioning

The architecture should be compared by concrete technical limitations rather than broad marketing statements. Counsel should conduct a formal prior-art search covering superconducting quantum processors, topological quantum computing, graph Hamiltonians, magnetic graph Laplacians, non-Abelian holonomy, fractal quantum walks, and subspace-encoded qubits.

No assertion in this document establishes novelty or non-obviousness against any particular commercial processor.

## 12. Enablement and Experimental Program

A complete hardware filing package should be supplemented with device drawings, fabrication stack, control electronics, calibration procedures, measurement protocol, numerical parameter sweeps, uncertainty budgets, and experimental data.

## 13. Disclosure Boundary

The current research repository establishes a mathematical and computational foundation. It does not establish that a physical QPU has been fabricated or that the candidate logical subspace is fault tolerant.
