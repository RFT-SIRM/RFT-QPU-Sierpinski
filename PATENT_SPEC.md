# RFT-QPU-Sierpinski — technical disclosure for patent-counsel review

**Handling:** private / confidential working document  
**Review date:** 11 November 2026  
**Project author attribution:** Evgeny Zaprudnov  
**Status:** technical disclosure draft; not a patent application, legal opinion, novelty search or grant.

This document consolidates technical subject matter already recorded in the RFT-QPU-Sierpinski repository. It is intended to help qualified patent counsel decide whether there are concrete, patentable technical embodiments and what additional disclosure or experimental work is required. It does not assert that the mathematical construction is patentable or that any patent has been filed.

## 1. Invention area and technical problem

The project studies a quantum-processing architecture in which a recursively generated Sierpiński-gasket graph carries an internal two-component degree of freedom and SU(2)-valued edge transport. The first proposed physical embodiment maps each graph site to a pair of superconducting transmon modes and realizes graph hopping through phase-controlled exchange interactions.

The technical problem is not merely the definition of a graph or a mathematical invariant. It is the construction, calibration and operation of a physical network whose effective single-excitation Hamiltonian implements a prescribed non-commuting transport pattern while maintaining a spectrally identifiable two-dimensional candidate subspace.

## 2. Technical architecture

### 2.1 Graph and internal space

For a finite graph G = (V,E), every site carries a two-component internal degree of freedom. The graph-model Hilbert space is C^|V| ⊗ C². Let D be the graph-degree operator and Uₐᵦ ∈ SU(2) the transport matrix on an oriented edge.

A representative effective Hamiltonian is:

H = D ⊗ I₂ − Σ(a,b) [ |a⟩⟨b| ⊗ Uₐᵦ + |b⟩⟨a| ⊗ Uₐᵦ† ].

A nominal edge transport is Uₐᵦ = exp(−i θ σ_axis / 2), with θ = π/2 and axis selected from X, Y or Z for designated face edges. The edge orientation, face ordering and axis assignment are part of the implementation convention and must be fixed in any claim or comparison.

### 2.2 Level-1 embodiment

The current level-1 graph mapping has:

| Item | Count |
|---|---:|
| Graph sites | 6 |
| Graph edges | 9 |
| Elementary faces | 3 |
| Selected non-commuting links | X, Y, Z |
| Transmon modes | 12 |
| Single-excitation sector dimension | 12 |
| Non-zero effective inter-site exchange channels | 22 |

Each graph site v is represented by two modes, labelled up and down. The logical model is restricted to total excitation number one. The two modes form a synthetic SU(2) degree of freedom; they are not two independently encoded logical qubits.

### 2.3 Link matrices and circuit mapping

At θ = π/2, with c = s = 1/√2, the project records:

- Ux = [[c, −i s], [−i s, c]];
- Uy = [[c, −s], [s, c]];
- Uz = [[c − i s, 0], [0, c + i s]].

The circuit Hamiltonian uses hopping coefficient −J Uₐᵦ. The current level-1 map has six identity edges and three selected face edges, resulting in 6×2 + 4 + 4 + 2 = 22 non-zero effective exchange channels.

Parametric exchange is proposed to set complex hopping phases through phase-locked drive tones. The repository's exact coefficient-to-channel mapping is retained in hardware/level1/couplers.csv; associated frequency and channel tables are in hardware/level1/.

### 2.4 Critical Z-link feasibility issue

The active Z edge joins two degree-4 sites in the initial degree-based frequency plan. It is therefore resonant in that plan, while the diagonal hopping coefficients require opposite non-real phases. A single real static resonant coupler cannot implement those phases.

Candidate engineering routes recorded in the repository are:

1. a multi-path/static-flux coupler network;
2. an auxiliary Floquet/parametric path that synthesizes the required phase;
3. a revised rotating-frame or frequency plan that changes the implementation constraints.

No route is yet closed by a fabricated device or measured experiment. This is a concrete technical blocker and must remain visible in any patent or partner packet. A claim directed to the phase-engineered implementation should not be drafted as if this issue had already been solved.

## 3. Logical subspace and controls

The candidate logical qubit is a selected two-dimensional low-energy eigenspace of the finite Hamiltonian, with projector P. Candidate controls are obtained by projection of physical/internal operators, for example P Oₓ(v) P, P Oᵧ(v) P and P O_z(v) P.

At level 1, the numerical model identifies vertex 5 as the best local control site, with local g_eff = 0.1770433 and full-rank projected axes in the ideal model. The global-control map also has rank three, with a larger smallest singular value but a greater routing and calibration burden.

The near-zero ideal doublet splitting is a floating-point numerical result, not a prediction of manufactured-device splitting. The reported Kramers-like degeneracy follows from an effective antiunitary symmetry of the mathematical rotating-frame Hamiltonian. It must not be represented as immunity to non-gauge laboratory noise or as physical time-reversal protection without a device-level demonstration.

## 4. Two-cell extension

The repository contains a static projection of two level-1 cells (24 data transmons). The target inter-cell term is a differential-density interaction whose projection gives coefficient 0.00783608327 χ. The 6.38074 μs estimate assumes χ/(2π) = 10 MHz.

This is an ideal static projection, not a pulsed, calibrated or measured entangling gate. A practical embodiment requires four pairwise cross-Kerr channels with sign pattern (+, −, −, +), followed by device-specific calibration, leakage and crosstalk measurements.

## 5. Circuit-derived three-mode gate model — Stage 11B

A separate Stage 11B model treats data transmon A, a SQUID coupler C and data transmon B as a three-mode circuit. It rebuilds the full three-mode product Hamiltonian in the local coupler eigenbasis re-quantized at shifted DC flux. This A–C–B gate model is distinct from the full 12-mode level-1 graph tile.

The tracked initial baseline uses charge cutoff 10, five retained levels per mode and a 125-dimensional product space. At 480 steps per pump period, the unchanged Stage-10 pulse yields projected process overlap after local-Z fitting 0.999991791082, with conditional phase 0.002216577957 rad. The baseline has tracked JSON and NPZ matrix artifacts and 120/240/480 time-grid comparisons.

A later local retune is recorded in the root README and in the local-retune note. Its selected five-level 480-grid result is projected process overlap 0.9999999793763371, average logical-state fidelity including leakage 0.9999999803654352, A→B 0.9999999973549074, B→A 0.999999992602828 and conditional iSWAP phase 0.00027739757232 rad. The six-level 480-grid process overlap is 0.999999967757. The raw retune JSON/NPZ outputs are not tracked in the repository; hashes are recorded, but those hashes do not reproduce the missing files.

These are closed-system numerical projections with nominal Stage-3 circuit assumptions. The reported process overlap is not an experimental gate fidelity.

## 6. Other engineering evidence relevant to a technical filing

- The finite-level study covers SG levels 1–5; level 5 maps to 732 transmons per cell under the current dual-rail mapping.
- The level-1 leakage gap is 1.3937127 J in the ideal dimensionless Hamiltonian.
- At the illustrative J/(2π) = 10 MHz, the level-1 gap is approximately 13.94 MHz. The repository's 10 mK thermal benchmark gives kBT/h ≈ 208.37 MHz and exp(−Δ/kBT) ≈ 0.935, so passive thermal protection is not established.
- The nine-tone graph-wide primary screen contains 73 warnings within 10 MHz, and the conditional harmonic/intermodulation screen contains 653 warnings. Simultaneous operation is not cleared.
- The local disorder study varies positive scalar edge weights with the corresponding weighted-degree diagonal. It does not model arbitrary fabrication, frequency, flux, pump-phase or open-system errors.

## 7. Potential claim groups for counsel to evaluate

These are discussion topics, not draft claims and not an assertion of patentability.

**A. Physical quantum-processing element.** A device whose physical modes are arranged in site pairs and whose engineered coupling network realizes a specified graph Hamiltonian with non-commuting internal transport matrices.

**B. Phase-engineered exchange network.** A specific coupler/control topology that generates calibrated complex hopping amplitudes, including a realizable solution for the resonant diagonal-phase edge.

**C. Calibration and phase-consistency method.** A control procedure for determining and maintaining complex link amplitudes/phases across a set of coupled channels, with a defined technical output such as a reconstructed effective Hamiltonian or loop transport.

**D. Logical-state preparation and control.** A physical procedure for preparing, tracking and controlling a specified two-dimensional low-energy subspace of the implemented graph Hamiltonian, with measured leakage and spectral criteria.

**E. Two-cell interaction.** A circuit topology and control sequence that implements the specified four-channel differential-density interaction between two logical cells and demonstrates an entangling operation.

**F. Device validation method.** A procedure combining measured spectra, calibrated complex couplings, projected control matrices and leakage criteria to accept or reject a physical implementation.

A claim to the abstract graph, SU(2) formula, spectral-moment identity, or mathematical invariant alone should not be assumed to be available. Patent counsel should focus on specific technical means and a technical effect supported by a sufficiently detailed implementation.

## 8. Alternative embodiments

The original project notes list superconducting circuits, semiconductor spin systems, trapped particles, photonic networks and synthetic quantum simulators as possible platforms. These are conceptual alternatives only. The detailed engineering work in this repository is for the proposed superconducting-transmon mapping; no alternative platform has been built or qualified here.

## 9. Evidence and exhibits already in the repository

| Exhibit | Location |
|---|---|
| Graph and architecture definition | docs/ARCHITECTURE.md |
| Physical mapping and coupler phase issue | engineering/physical_prototype/docs/PHYSICAL_REALIZATION.md |
| Level-1 topology diagram | engineering/physical_prototype/design/level1_transmon_topology.svg |
| Channel coefficients | engineering/physical_prototype/hardware/level1/ |
| Finite-level results | engineering/physical_prototype/results/RESULT_SUMMARY.md |
| Two-cell projection | engineering/physical_prototype/results/two_cell_entangler_report.json |
| Pump-collision audit | engineering/physical_prototype/docs/FLOQUET_COLLISION_AUDIT.md |
| Stage 11B baseline | engineering/physical_prototype/docs/STAGE11B_REQUANTIZED_GATE.md |
| Stage 11B baseline JSON/NPZ | engineering/physical_prototype/results/stage11b_requantized_gate.json and stage11b_requantized_gate_matrices.npz |
| Stage 11B local-retune record | engineering/physical_prototype/docs/STAGE11B_LOCAL_RETUNE_NOTE.md |

## 10. Filing and disclosure status

At the repository review date, no patent application number, filing date, patent office, priority claim or granted patent is recorded in this repository. That is not evidence about documents held elsewhere.

Before filing or external disclosure, counsel should:

1. determine all actual inventors by contribution to the subject matter of each proposed claim;
2. establish ownership and assignment for all relevant source, drawings, data and inventions;
3. conduct prior-art and freedom-to-operate searches;
4. determine whether the proposed claims have technical character, novelty, inventive step and sufficient disclosure in each target jurisdiction;
5. resolve the complex Z-link implementation or define a clearly bounded alternative embodiment;
6. prepare device drawings, circuit schematics, parameter tables, control sequences, calibration procedures and alternative embodiments;
7. verify the disclosure chronology, including any previous presentations, websites, repositories, emails, demonstrations or discussions without confidentiality.

## 11. Legal references for counsel

- WIPO, How to Protect Inventions through Patents: https://www.wipo.int/en/web/patents/protection
- WIPO, Patent FAQs: https://www.wipo.int/en/web/patents/faq_patents
- WIPO, Technology Transfer FAQs: https://www.wipo.int/en/web/technology-transfer/faq
- EPO, 2026 Guidelines — Mathematical methods: https://www.epo.org/en/legal/guidelines-epc/2026/g_ii_3_3.html
- EPO, 2026 Guidelines — Simulation, design or modelling: https://www.epo.org/en/legal/guidelines-epc/2026/g_ii_3_3_2.html

WIPO guidance warns that non-confidential pre-filing disclosure can destroy novelty in many jurisdictions; grace periods differ by jurisdiction and subject matter. EPO guidance distinguishes mathematical methods as such from implementations that make a technical contribution. This summary is not legal advice. All filing decisions and claim language must be made with qualified patent counsel.
