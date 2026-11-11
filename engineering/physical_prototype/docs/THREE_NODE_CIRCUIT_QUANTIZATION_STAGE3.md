# Three-node circuit quantization — Stage 3

## Purpose

Stage 2 used free Duffing-mode coupling parameters and a sinusoidal frequency
modulation parameter. Stage 3 connects those effective quantities to a
specified three-node circuit: data transmon A — asymmetric SQUID transmon
coupler C — data transmon B.

The model constructs a nodal capacitance matrix, inverts it to obtain the full
charging-energy matrix, quantizes each isolated Josephson mode in a charge
basis, calibrates the isolated 0-1 frequencies, and then diagonalizes the
coupled three-qutrit product Hamiltonian. The SQUID effective Josephson energy
and phase offset are flux dependent.

## Declared nominal assumptions

| Quantity | Assumption |
|---|---:|
| A / C / B target 0-1 frequencies | 5500 / 5007.5 / 4515 MHz |
| Nominal A / C / B charging energies | 250 / 300 / 250 MHz |
| A-C mutual capacitance | 0.70 fF |
| C-B mutual capacitance | 0.75 fF |
| A-B parasitic capacitance | 0.03 fF |
| SQUID total Josephson energy | 18 GHz (in frequency units) |
| SQUID junction asymmetry | 0.05 |
| Charge-basis cutoff | 8 |
| Local levels retained | 3 per mode |

These are explicit study assumptions, not extracted layout parameters. In
particular, the capacitances, SQUID asymmetry, EJ sum and DC flux must later be
replaced by values from an actual layout / fabrication target.

## Nominal static result

- DC SQUID flux bias: `0.26684368 Phi_0`.
- Local 0-1 frequencies: `5500`, `5007.5`, `4515 MHz` (numerically calibrated).
- Local anharmonicities: approximately `-277.88`, `-344.28`, `-286.43 MHz`.
- Charge-derived 0-1 exchange matrix elements: `g_AC = 25.562 MHz`,
  `g_CB = 24.803 MHz`, direct parasitic `g_AB = 1.208 MHz`.
- Dressed A-B transition separation: `987.576 MHz`.
- Residual static ZZ from dressed energies: `-3.280 kHz`.
- Minimum overlap of the tracked dressed states with their bare product
  states: approximately `0.99475`.

The static ZZ is `E_11 - E_10 - E_01 + E_00`. It is not the driven ZZ during a
parametric gate.

## Flux-to-frequency calibration

At the nominal bias, the local coupler slope is approximately
`-9279 MHz / Phi_0`. The nonlinear SQUID curve gives the following peak shifts:

| Flux amplitude | Negative peak shift | Positive peak shift |
|---:|---:|---:|
| 0.005 Phi0 | +45.9 MHz | -46.9 MHz |
| 0.010 Phi0 | +90.7 MHz | -94.9 MHz |
| 0.020 Phi0 | +177.3 MHz | -194.2 MHz |
| 0.030 Phi0 | +259.9 MHz | -298.0 MHz |

The asymmetry is intentional: a flux waveform does not map to a perfectly
sinusoidal frequency modulation. A 300-400 MHz parameter in the Stage-2
Duffing model must not be mistaken for a calibrated flux-line amplitude.

## Convergence checks

For `C_AC = 0.70 fF`, `C_CB = 0.75 fF`, `C_AB = 0.03 fF`:

| Charge cutoff | Local levels | g_AC (MHz) | g_CB (MHz) | Static ZZ (kHz) |
|---:|---:|---:|---:|---:|
| 6 | 3 | 25.5616 | 24.8027 | -3.2794 |
| 8 | 3 | 25.5620 | 24.8028 | -3.2797 |
| 10 | 3 | 25.5620 | 24.8028 | -3.2797 |
| 8 | 4 | 25.5620 | 24.8028 | -3.2780 |

This checks numerical truncation for this declared parameter point. It does
not validate the parameter assumptions or the physical layout.

## Model boundary and next gate

This is a static, charge-basis circuit quantization study. It does not yet
simulate a time-dependent SQUID flux pulse, nonadiabatic coupler-basis motion,
flux-line transfer distortion, dissipation, thermal population, fabrication
disorder, spectator modes, or the complete 22-channel network.

Next: replace the assumed capacitance/Josephson parameters with extracted
layout values, then derive a time-dependent circuit Hamiltonian using the
actual flux waveform. Only after that should a dynamic gate be evaluated and
compared with Stage-2 effective Duffing results.
