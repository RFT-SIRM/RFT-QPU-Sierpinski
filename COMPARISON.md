# Technology Comparison — Architecture, Not a Performance Ranking

This table is intended for investor and partner discussions. It compares architectural objects and development requirements without declaring a winner or claiming experimentally demonstrated superiority.

| Dimension | Classical CPU / GPU | Mainstream superconducting QPU | RFT-QPU-Sierpinski research architecture |
|---|---|---|---|
| Physical substrate | Transistors and memory | Superconducting circuits, resonators, control/readout hardware | Candidate physical system implementing a self-similar graph Hamiltonian |
| Basic computational element | Bit / vector lane / tensor operation | Physical qubit | Candidate two-dimensional low-energy subspace |
| Connectivity | Electronic interconnect / memory hierarchy | Device-specific qubit coupling graph | Sierpiński-gasket or related self-similar graph |
| Internal structure | Digital voltage/current states | Quantum two-level systems | Two-component internal SU(2) degree of freedom |
| Transport/control structure | Classical gates and instructions | Microwave/flux/control pulses | SU(2)-valued edge transport plus projected controls |
| Logical operation | Instruction / arithmetic operation | Calibrated quantum gate | Candidate projected operator `P S P` |
| Mathematical anchor | Boolean/algebraic computation | Device Hamiltonian + calibration model | Gauge-covariant spectral-moment construction |
| Error protection | Classical redundancy / ECC | Quantum error correction and calibration | Proposed spectral/subspace protection mechanisms requiring validation |
| Current evidence in this project | N/A | External commercial technology | Numerical research architecture; not experimentally validated |
| Main open engineering question | Energy/performance scaling | Fidelity, coherence, control, scaling | Realizable Hamiltonian, gap, leakage, controls, disorder, noise and scaling |

## Important wording for presentations

Use:

- “candidate logical qubit”;
- “research architecture”;
- “spectral invariant”;
- “gauge-covariant construction”;
- “proposed protection mechanism”.

Avoid presenting `I∞ = −8/9` as an energy gap or presenting gauge covariance as proof of arbitrary-noise immunity.
