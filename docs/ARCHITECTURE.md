# RFT-QPU-Sierpinski architecture

## 1. Mathematical-to-hardware mapping

The level-1 Sierpinski-gasket graph has six vertices, nine edges and three elementary face transports. Each graph vertex is represented by a dual-rail pair of transmon modes, giving 12 data modes. The effective single-excitation Hamiltonian encodes the graph onsite degree term and complex SU(2) edge transports.

At J/(2π)=10 MHz the finite model gives a leakage gap of 1.3937126931 J and a best local projected-control coefficient of 0.1770433 at vertex 5. These are numerical model values, not measured device properties.

## 2. Proposed transmon block

The coefficient export contains 22 nonzero effective exchange channels. It is a control target, not a physical netlist. The physical implementation must account for coupler modes, nonlinearities, residual exchange and ZZ, pump-line transfer, resonators, package modes and loss.

## 3. Complex-Z link: isolated reduced-model candidate

The active Z edge joins equal-degree sites, so the target onsite detuning is zero. Its diagonal hopping coefficients have phases +135° and −135°. The isolated-link candidate uses a signed rotating-frame difference of −245 MHz, a 245 MHz parametric reference and phase-conjugate drives.

A two-Duffing-qutrit model and a four-qutrit block propagate the two channels concurrently. The reduced block reports one-excitation process overlap 0.999609 and N=2 population outside the computational qutrit subspace 1.17×10^-5. These are effective-Hamiltonian simulation outputs, not gate fidelities.

## 4. Full pump schedule: collision-screen failure

The nine-tone first-order collision screen reports:
- minimum primary resonance margin: 0 MHz;
- primary warnings within 10 MHz: 73;
- conditional harmonic/intermodulation warnings: 653.

The screen compares both rotating-frame sidebands with N=1 exchange and Duffing-qutrit N=2 transitions. It does not predict transition probabilities because the actual channel-to-channel drive transfer functions are unknown. Nevertheless, the zero-margin candidates mean that the present nine-tone schedule is not cleared for simultaneous operation.

Before tape-out:
1. redesign the six local rotating-frame offsets with a declared guard band;
2. measure/extract the complex 22×22 pump-channel transfer matrix;
3. build an explicit data–coupler–data circuit model;
4. run full multitone Floquet, residual-ZZ, spectator, leakage, EM and open-system validation.

The current CSV is a coefficient map, not a foundry-ready netlist. See [the collision audit](../engineering/physical_prototype/docs/FLOQUET_COLLISION_AUDIT.md).

## 5. Evidence boundary

No chip has been fabricated or measured. The candidate logical doublet, projected controls, phase-conjugate link and two-cell interaction remain numerical/model results. No measured gate fidelity, thermal protection, arbitrary-noise immunity or fault tolerance is claimed.
