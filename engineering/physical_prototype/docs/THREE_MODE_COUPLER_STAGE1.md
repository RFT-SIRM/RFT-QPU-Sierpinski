# Stage 1 — explicit three-mode nonlinear coupler model

## Scope

This stage replaces a purely effective A–B exchange coefficient with an
explicit `transmon A — nonlinear coupler C — transmon B` model. It is a
three-Duffing-mode effective rotating-frame model, with a sinusoidal
modulation of the coupler frequency. It is **not yet** a circuit-quantized
capacitance/Josephson/SQUID model or a fabrication netlist.

The Hamiltonian is

\[
H(t)/\hbar = \sum_{j\in\{A,C,B\}}\left[\Delta_j n_j +
\frac{\alpha_j}{2}n_j(n_j-1)\right]
+g_{AC}(a^\dagger c+c^\dagger a)
+g_{CB}(c^\dagger b+b^\dagger c)
+\delta_c\cos(\omega_p t+\phi_p)n_C.
\]

All frequencies are in MHz. The calculation separately treats the total
excitation `N=1` and `N=2` sectors, preserving excitation number in this toy
Hamiltonian. It builds a truncated Sambe matrix for the driven system,
extracts the effective complex exchange, computes the static dressed ZZ
shift, and integrates the time-dependent Schrödinger equation for a one-
and two-excitation stress test.

## Initial stress point (not a selected hardware design)

- Bare data-mode separation: 985 MHz.
- Coupler placed at the midpoint of the data frequencies.
- Data anharmonicities: -250 and -245 MHz.
- Coupler anharmonicity: -300 MHz.
- Both capacitive exchange couplings: 100 MHz.
- Coupler frequency-modulation amplitude: 200 MHz.

The model tunes the pump frequency to the dressed resonance; the result is
not forced to equal the bare 985 MHz separation. This is intentional: a
coupler's AC-Stark/dispersive dressing shifts the actual resonance condition.

## Interpretation

A high one-excitation swap probability is not sufficient. The `N=2` stress
state starts in `|1_A,0_C,1_B>` and measures population leaving that logical
state during the same pulse. That lost population includes coupler excitation
and higher-level occupation; it is an engineering leakage warning, not a
measured device error.

Do not tune a real chip from these numbers. The next physical-model step is
to derive the capacitance matrix and nonlinear Josephson/SQUID potential,
quantize the circuit, extract flux-dependent mode frequencies/couplings and
then rerun this Floquet/dynamic analysis with the actual parameter map.
