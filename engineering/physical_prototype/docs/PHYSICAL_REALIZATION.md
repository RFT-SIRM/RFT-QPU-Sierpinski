# Physical realization: transmon spinor network

## 1. Mathematical object to be implemented

The reference model has a finite graph `G=(V,E)`. Each vertex carries a two-component internal state, so the one-excitation Hilbert space is

`H_1 = C^{|V|} tensor C^2`.

For an undirected edge `(a,b)` with `a < b`, the Hamiltonian is

`H/J = D tensor I_2 - sum_(a,b in E) ( |a><b| tensor U_ab + |b><a| tensor U_ab^dagger )`,

where `D` is the graph degree matrix and `U_ab` is either the identity or one of

`U_ab = exp(-i theta sigma_axis / 2)`, `axis in {x,y,z}`.

The canonical face recursion and edge orientation are taken from the existing `Evgeny-Theorem` reference implementation. One designated edge per elementary face receives a transport; its Pauli axis cycles by face index `0,1,2,0,1,2,...`. This convention is not interchangeable with another triangular-lattice graph or a reordering of faces.

## 2. Circuit encoding

Each graph vertex `v` is represented by a pair of weakly anharmonic microwave modes (implemented as two transmons):

- `q_v_up` represents `|v, up>`;
- `q_v_dn` represents `|v, down>`.

The logical simulation is restricted to the single-excitation sector

`sum_v (n_v_up + n_v_dn) = 1`.

In that sector, the pair of modes at a site is the synthetic SU(2) degree of freedom. It is not a claim that the two transmons are themselves one independent logical qubit each.

A useful effective rotating-frame Hamiltonian is

`H_eff/hbar = sum_v d_v J (n_v_up+n_v_dn)`

`              - sum_(a,b) sum_(s,t) [ J (U_ab)_(s,t) a^dagger_(a,s) a_(b,t) + h.c. ]`

`              - sum_i (alpha_i/2) n_i(n_i-1) + H_readout + H_residual`.

The onsite term realizes the graph degree matrix. The hopping matrix realizes the SU(2) link. Transmon anharmonicity is irrelevant in the exact one-excitation subspace but helps suppress unwanted higher-excitation occupation during imperfect control and readout.

The effective model is valid only after checking the rotating-wave approximation, parametric-drive sidebands, residual ZZ, spectator couplings, leakage to higher transmon levels, and drift of pump phases.

## 3. Mapping each SU(2) edge to couplers

For `theta=pi/2`, let `c=s=1/sqrt(2)`. The three link matrices are

`U_x = [[c, -i s], [-i s, c]]`,

`U_y = [[c, -s], [s, c]]`,

`U_z = [[c-i s, 0], [0, c+i s]]`.

The hopping coefficient in the circuit Hamiltonian is `-J U_ab`. Therefore:

- an identity edge uses two spin-preserving exchange channels, each of amplitude `J`;
- an X edge uses four channels, each of amplitude `J/sqrt(2)`, with the phases in `-U_x`;
- a Y edge uses four channels, each of amplitude `J/sqrt(2)`, with the phases in `-U_y`;
- a Z edge uses two spin-preserving channels, each of amplitude `J`, with phases `+/- 3 pi/4` or the equivalent calibrated convention.

At SG level 1 there are six identity edges and one face edge for each of X, Y and Z, giving `6*2 + 4 + 4 + 2 = 22` nonzero effective exchange channels.

The generated `hardware/level1/couplers.csv` is the exact coefficient-to-channel map for the project's sign convention. It also computes the endpoint detuning implied by the degree-based frequency plan. The active Z edge at level 1 connects two degree-4 sites and is therefore resonant in the initial plan, while its two diagonal hopping amplitudes have non-real phases. A single real static coupler cannot implement those phases. That channel needs a multi-path static-flux circuit, an auxiliary Floquet path, or a re-optimized rotating-frame/frequency plan. This is an explicit pre-tape-out blocker; do not treat the CSV as a foundry-ready netlist. A fabrication netlist must preserve the complex phase, not only the absolute coupling.

## 4. How to create complex hopping

The proposed implementation is a tunable-coupler transmon array with parametric exchange. A flux or microwave pump at the difference frequency between two modes activates a number-conserving exchange term; the pump phase sets the complex phase of the effective hopping coefficient. Phase-locked pumping is required for all links that form the same SU(2) matrix.

This method has experimental precedent for flexible parametric coupling between transmons, but the 22-channel SG pattern and its simultaneous calibration have not been demonstrated by this project. Each link requires calibration of amplitude, phase, parasitic ZZ, off-resonant sidebands and spectator effects.

## 5. Intra-site logical controls

At one graph site, define number-conserving Pauli-like mode operators

`O_x(v) = a^dagger_(v,up) a_(v,dn) + a^dagger_(v,dn) a_(v,up)`,

`O_y(v) = -i a^dagger_(v,up) a_(v,dn) + i a^dagger_(v,dn) a_(v,up)`,

`O_z(v) = n_(v,up)-n_(v,dn)`.

The angular-momentum convention is `S_alpha(v)=O_alpha(v)/2`. X/Y are the two quadratures of an intra-site parametric beam-splitter link; Z is a differential frequency (flux) bias. These controls preserve the total excitation number in the ideal model.

The logical control operators used by the simulator are `P O_alpha(v) P`. In the current numerical convention the best level-1 local site is vertex 5 at coordinate `(0,1)`. Its three projected axes have equal singular value `g_eff = 0.1770433085` and full rank. A physical drive `H_drive/hbar = (Omega/2) O_alpha` therefore has logical rotation rate scaled by `g_eff`; the projected angular-momentum operator `P S_alpha P` has scale `g_eff/2`. A phase-aware local calibration maps physical drive axes into the logical Bloch sphere.

A global alternative applies the same `O_alpha` control to all graph sites. Its smallest projected singular value is 0.87685668 at level 1, but it requires simultaneous calibrated control over all six site pairs.
## 6. Readout and initialization

The one-excitation logical state is distributed over the 12 physical modes. The device needs:

1. reset all transmons to their ground states;
2. prepare one excitation in a calibrated starting mode;
3. adiabatically or digitally map it into the selected logical doublet;
4. apply calibrated projected controls;
5. measure mode occupations and selected interference observables;
6. reconstruct the logical Bloch vector and leakage probability.

Dispersive readout resonators are proposed for each transmon, with multiplexing introduced only after crosstalk and assignment error have been characterized. The exact one-excitation manifold is not directly observable from a single occupation measurement; state tomography and calibration of the measurement map are required.

## 7. Symmetry and the doublet

For the ideal spinor Hamiltonian, define `T = (I_graph tensor i sigma_y) K`, where `K` is complex conjugation. The SU(2) identity `sigma_y U* sigma_y = U` yields `T H T^-1 = H` and `T^2=-I`. This gives a Kramers-like double degeneracy in the mathematical model.

Because the circuit's SU(2) degree of freedom is a synthetic mode label and its link phases are pump-engineered, this should be described as an **effective antiunitary symmetry of the rotating-frame model**, not automatically as microscopic time-reversal symmetry of the driven device. Pump-phase drift, spin-dependent frequency shifts, non-SU(2) coupling errors and magnetic/control fields can break the effective symmetry and split the doublet.

## 8. What this mapping does not prove

The mapping does not establish that the proposed hardware can achieve the required simultaneous couplings, that the gap survives fabrication and drive imperfections, that the doublet has a long coherence time, or that a multi-cell entangling gate works. Those are validation gates, not assumptions.
