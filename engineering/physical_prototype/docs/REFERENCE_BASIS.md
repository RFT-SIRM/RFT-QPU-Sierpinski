# Reference basis and evidence separation

## Project-derived mathematical source

The graph recursion, vertex/face ordering, SU(2) transport, face-index axis convention and gauge law are ported from the current reference code in `RFT-SIRM/Evgeny-Theorem` (`src/graph/sg_graph.py`, `src/operators/operators.py`, `src/su2/su2_utils.py`, and the corresponding Lean graph/face definitions). The QPU repository's original `qpu_core.py` is a minimal two-site numerical core; the new package is a full finite-SG research solver, not a replacement for the theorem repository.

The finite model in this package is the QPU's two-component SU(2)-transport graph Hamiltonian. It is **not** the signed Z2-flux operator used in the separate Phi-Genesis Schur/spectral-gap line. Those operator families must not be conflated.

## External hardware precedent (not proof of this device)

1. A. Mezzacapo et al., “Non-Abelian SU(2) Lattice Gauge Theories in Superconducting Circuits,” *Physical Review Letters* 115, 240502 (2015), DOI: https://doi.org/10.1103/PhysRevLett.115.240502. This is a proposal for simulating non-Abelian SU(2) gauge dynamics using superconducting circuits; it is not an experimental demonstration of the RFT-SG Hamiltonian.
2. X. Jin et al., “Versatile parametric coupling between two statically decoupled transmon qubits,” *Nature Physics* (2023), NIST publication record: https://www.nist.gov/publications/versatile-parametric-coupling-between-two-statically-decoupled-transmon-qubits. NIST reports parametric coupling between transmons, including driven-swap and swap-free controlled-Z operation. This supports the availability of the general control primitive, not the 22-channel SU(2) netlist proposed here.
3. “Synthetic gauge field and chiral physics on two-leg superconducting circuits,” *Physical Review A* 102, 032610 (2020), DOI: https://doi.org/10.1103/PhysRevA.102.032610. This work describes synthetic gauge phases in a superconducting-circuit model using microwave drives. It is a relevant control precedent, not proof of the specific SG architecture.
4. “Optimizing the Frequency Positioning of Tunable Couplers in a Circuit QED Processor to Mitigate Spectator Effects on Quantum Operations,” *Physical Review Letters* 136, 200801 (2026), DOI: https://doi.org/10.1103/wdfj-4nbt. This highlights coupler-frequency placement, spectator interactions and residual coherent couplings as real processor-design constraints relevant to this proposed layout.

## What is calculated here

- SG level 1–5 graph and matrix sizes;
- ideal finite spectra at `theta=pi/2`;
- ideal doublet splitting and gap to the next eigenstate;
- projected local and global control matrices;
- coupling channel count and coefficient/phase export;
- scalar edge-weight disorder and deliberately time-reversal-breaking local-field sensitivity;
- illustrative thermal energy-scale comparison.

## What remains a hardware hypothesis

All transmon frequencies, `J/(2 pi)`, parametric pump implementation, readout count, coupler type, entangling interaction and packaging quantities are design assumptions. None has been fabricated or measured by this project. External papers show that related circuit-QED primitives exist; they do not validate this particular device.
