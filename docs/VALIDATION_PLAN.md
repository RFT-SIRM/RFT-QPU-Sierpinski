# Validation plan

## Gate 0 — numerical software

- [x] Finite graph and SU(2) transport regressions.
- [x] Hermiticity, spectrum and projected-control checks.
- [x] Two-cell projected interaction calculation.
- [x] Reduced qutrit and concurrent phase-conjugate Z-link simulations.
- [x] Deterministic first-order nine-tone collision screen.

## Gate 1 — frequency and control feasibility

**Current result: FAIL / redesign required.**

- Current plan: six sites, nine pump references, 22 effective exchange channels.
- Isolated 245 MHz Z-link candidate: reduced four-qutrit process overlap 0.999609.
- Full schedule primary collision margin: 0 MHz.
- Primary warnings within 10 MHz: 73.
- Conditional harmonic/intermodulation warnings: 653.

The isolated-link result does not authorize simultaneous nine-tone operation.

Required next work:
1. redesign the six rotating-frame offsets while preserving the graph onsite term;
2. define a primary collision guard band and rerun the audit;
3. measure/extract the complex 22×22 pump-channel transfer matrix;
4. include the actual coupler flux-to-exchange/ZZ transfer function;
5. run multitone Floquet and open-system simulations.

## Gate 2 — physical circuit

- [ ] Explicit data–coupler–data circuit Hamiltonian with extracted capacitance and Josephson parameters.
- [ ] Coupler modes, anharmonicities, loss and flux dependence.
- [ ] Residual static/dynamic ZZ, Stark shifts and higher sidebands.
- [ ] Spectator transitions and all 22 effective channels.
- [ ] EM/package extraction and control/readout layout.

## Gate 3 — fabricated one-cell demonstrator

- [ ] Fabricate and spectroscopically identify the 12 modes.
- [ ] Calibrate complex amplitudes and phases with uncertainty bars.
- [ ] Measure the spectrum and candidate doublet.
- [ ] Reconstruct projected controls and measure leakage/coherence.
- [ ] Repeat across cooldowns and quantify drift.

A green numerical test suite is Gate 0 only. It does not establish a fabricated or functioning QPU.
