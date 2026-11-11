# Three-mode coupler optimization — stage 2

## Purpose

Stage 1 established an explicit effective Duffing-mode stress model. Stage 2
searches a bounded parameter grid and re-runs time-domain dynamics on a short
list. It does not turn the effective model into a fabrication-ready circuit.

## Search space

- Symmetric capacitive exchange: `g_AC = g_CB` in `{20, 25, 30, 35} MHz`.
- Coupler frequency-modulation amplitude in `{150, 200, 250, 300, 350, 400} MHz`.
- Coupler Duffing anharmonicity in `{-200, -300, -400} MHz`.
- 72 static Sambe/static-ZZ points, with Sambe order 4.
- Six shortlisted points receive time-domain N=1 and N=2 propagation.

The screening thresholds in the JSON are provisional comparison thresholds,
not device specifications or experimental acceptance criteria.

## Observed trade-off

Representative dynamic points from the present model:

| g (MHz) | modulation (MHz) | J_eff (MHz) | N=2 leakage | static ZZ (MHz) | swap time (ns) |
|---:|---:|---:|---:|---:|---:|
| 20 | 400 | 0.3112 | 0.684% | -0.000723 | 805.4 |
| 25 | 300 | 0.3729 | 0.559% | -0.001764 | 664.7 |
| 25 | 350 | 0.4303 | 0.981% | -0.001764 | 581.9 |
| 25 | 400 | 0.4855 | 0.810% | -0.001764 | 509.1 |
| 30 | 200 | 0.3634 | 0.759% | -0.003659 | 688.4 |
| 30 | 300 | 0.5359 | 1.318% | -0.003659 | 465.8 |

These figures are reproducible outputs of the stated effective model. They
are not measured gate errors, and the listed modulation amplitude is a
frequency-modulation parameter in MHz, not a calibrated flux amplitude.

## Sambe convergence

For `(g, modulation) = (25, 350) MHz`, the extracted exchange converges as:

| Sambe order | Pump (MHz) | J_eff (MHz) |
|---:|---:|---:|
| 2 | 987.327331 | 0.4301368903 |
| 3 | 987.327656 | 0.4302767553 |
| 4 | 987.327657 | 0.4302772628 |
| 5 | 987.327657 | 0.4302772638 |
| 6 | 987.327657 | 0.4302772638 |

Order 4 is sufficient for this candidate within the displayed precision.

## Important interpretation

The scan exposes a speed/leakage/ZZ trade-off. The fastest tested points are
not necessarily the lowest-leakage points. In particular, increasing the
coupling to 30 MHz and modulation to 300–400 MHz shortens the exchange time
but pushes the N=2 leakage above 1% in this model.

The current Duffing model also has no mapping from the frequency-modulation
amplitude to an applied flux waveform. A 350–400 MHz frequency swing cannot
be treated as a hardware control setting without deriving the SQUID
`E_J(Phi)` curve, its bias point, asymmetry, flux-line transfer function,
and the time-dependent circuit Hamiltonian.

## Next physical gate

Build a circuit-quantized three-node model from a declared capacitance matrix
and Josephson/SQUID potential. Extract the dressed 0-1 and 1-2 transitions,
flux-dependent couplings, residual ZZ and pump matrix elements; then repeat
Floquet and dynamic propagation using the actual flux waveform. Only after
that comparison should a point be carried into the 12-transmon tile.
