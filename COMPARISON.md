# Technology comparison — architecture, noise and evidence

**Purpose:** factual comparison for internal engineering and partner discussions. This is not a vendor ranking and does not claim that RFT-QPU-Sierpinski outperforms existing quantum processors.

## 1. What is being compared

RFT-QPU-Sierpinski is a proposed logical architecture and graph Hamiltonian. Its first physical embodiment is itself based on superconducting transmons. It is therefore not a separate physical platform equivalent to a trapped-ion, neutral-atom or photonic processor.

The meaningful comparison is between:
- conventional device-level qubit architectures and their calibration/error-management requirements;
- the graph-structured SU(2) encoding proposed here;
- the numerical evidence currently available in this repository.

## 2. Platform-level context

| Platform family | Typical architecture strengths | Important error/noise channels to manage | Relation to this project |
|---|---|---|---|
| Superconducting transmons | Fast microwave/flux control; chip-scale integration; tunable interactions | Energy relaxation (T1), dephasing (T2), flux noise, leakage to higher levels, residual ZZ, spectator coupling, pump/crosstalk, readout error and calibration drift | Directly relevant: the first RFT embodiment uses transmon modes and tunable/parametric couplers |
| Trapped ions | Long-lived internal states and flexible ion connectivity | Motional heating, mode crowding, laser intensity/phase noise, spontaneous emission, addressing crosstalk and gate-time accumulation | Alternative substrate; no ion embodiment is implemented in this repository |
| Neutral atoms / Rydberg arrays | Large configurable arrays and geometry programmability | Atom loss, finite Rydberg lifetime, laser phase/intensity noise, position variation, blockade imperfections and state-preparation error | Alternative substrate; only listed as a possible conceptual embodiment |
| Photonic systems | Optical networks and photonic routing; potentially low thermal load at the optical component | Photon loss, source/detector efficiency, indistinguishability, phase stability and multiplexing loss | Alternative substrate; no photonic model or prototype is included |
| Classical CPU/GPU | Mature deterministic computation and scalable control/analysis infrastructure | Not quantum-coherence noise; limits include power, memory bandwidth and classical approximation error | Required control, simulation and compiler infrastructure; not a direct quantum-device competitor |

The error-channel list is platform context, not measured data for a named vendor or device generation.

## 3. Evidence available for RFT-QPU-Sierpinski

| Quantity | Current repository result | What it means | What it does not mean |
|---|---:|---|---|
| Level-1 leakage gap | 1.3937127 J | Ideal finite graph Hamiltonian separation from the next level | Measured chip gap or thermal protection |
| Candidate doublet splitting | About 3.28 × 10⁻¹⁵ J | Floating-point near-degeneracy of the ideal graph model | Exact manufactured-device degeneracy |
| Local projected-control scale | 0.1770433 at level 1, vertex 5 | Ideal projected-control coefficient | Calibrated physical Rabi rate or gate speed |
| Stage 11B five-level process overlap | 0.999999979376 | Local-Z-fitted closed-system A–coupler–B projection at 480 steps/period | Measured gate fidelity or complete 12-transmon cell performance |
| Stage 11B six-level process overlap | 0.999999967757 | Cross-level numerical spot check at the same selected point | Full retained-level convergence |
| Maximum sampled logical leakage | 3.312 × 10⁻⁴ | Sampled leakage in the retuned three-mode closed-system pulse | Continuously bounded leakage or hardware leakage |
| Maximum sampled coupler-excited population | 6.090 × 10⁻³ | Sampled population of the coupler mode in the three-mode model | Direct physical coupler measurement |
| Graph-wide pump screen | 73 primary and 653 conditional warnings | Current first-order resonance-candidate screen | Measured error probability or full Floquet solution |
| Two-cell interaction coefficient | 0.00783608327 χ | Static projected interaction coefficient | Executed two-logical-qubit gate |

The local Stage 11B retune data are reported in the root README. Their raw fine-retune JSON/NPZ files are not tracked; see the Stage 11B local-retune note.

## 4. Noise comparison: what is and is not covered

### Noise/error channels represented in the current RFT work

- A finite graph Hamiltonian and a candidate low-energy subspace.
- Ideal projected local/global control matrices.
- A limited positive scalar edge-weight disorder study with the matching weighted-degree diagonal.
- A local-z perturbation study that deliberately breaks the effective antiunitary symmetry.
- Closed-system, coherent three-mode gate propagation.
- Sampled leakage and coupler-excitation diagnostics.
- A first-order pump/sideband resonance screen and conditional harmonic/intermodulation candidates.

### Noise/error channels not yet represented by measured or validated device data

- T1 energy relaxation and T2 dephasing.
- Thermal bath population and driven thermal transitions.
- Qubit/coupler frequency drift and flux noise.
- Measured flux-line transfer functions, filtering, delay and pulse distortion.
- Pump phase noise, amplitude noise and phase-reference drift.
- Full channel-to-channel crosstalk and spectator response.
- Fabrication distributions, layout-extracted parasitics and EM effects.
- Readout assignment error, reset error and state-preparation error.
- Correlated errors across simultaneous logical operations.
- Open-system two-cell gate performance.

### Specific caution on the current thermal scale

At the illustrative J/(2π) = 10 MHz, the level-1 gap is about 13.94 MHz. The repository's 10 mK benchmark gives kBT/h ≈ 208.37 MHz and an equilibrium Boltzmann factor exp(−Δ/kBT) ≈ 0.935. This indicates that passive thermal suppression is not established at that illustrative scale. It is a model benchmark, not a measured population in a fabricated device.

## 5. Why the headline numbers cannot be ranked against vendor fidelities

The Stage 11B process overlap is obtained from a closed-system numerical propagator, projection onto four chosen states and a local-Z fit. Commercial hardware results are normally obtained under physical calibration and measurement protocols that include state preparation, readout, leakage, drift and noise in device-dependent ways.

A valid comparison requires a common protocol, the same gate definition and a declared treatment of SPAM, leakage, coherent error, drift and uncertainty. Until then:

- do not call the Stage 11B process overlap a physical gate fidelity;
- do not compare it numerically with randomized benchmarking, cycle benchmarking or logical error rates;
- do not claim superior coherence, lower noise or built-in error correction;
- compare architecture and open engineering gates only.

## 6. Engineering decision

The best-supported next step is not a large-scale processor claim. It is a level-1 physical demonstrator programme that resolves the complex Z edge, clears the pump plan, replaces assumed circuit values with layout-extracted values, and measures the spectrum, projected controls, leakage, T1/T2, readout and calibration stability. A two-cell entangler follows only after the first tile is measured.

## 7. Project references

- [Architecture](docs/ARCHITECTURE.md)
- [Physical realization](engineering/physical_prototype/docs/PHYSICAL_REALIZATION.md)
- [Risk register](engineering/physical_prototype/docs/RISK_REGISTER.md)
- [Validation plan](docs/VALIDATION_PLAN.md)
- [Stage 11B local-retune note](engineering/physical_prototype/docs/STAGE11B_LOCAL_RETUNE_NOTE.md)
