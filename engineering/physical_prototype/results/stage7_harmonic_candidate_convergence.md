# Stage 7 harmonic waveform convergence

- Frequency: 987.513679799316 MHz
- Fundamental amplitude: 0.020000000 Phi0
- Second harmonic (cos, sin): (+0.000200000, +0.000000000) Phi0
- Shared physical duration: 1.062567558773707 us

| Steps/period | Transfer A->B | Process overlap | Conditional phase (rad) | Final leakage |
|---:|---:|---:|---:|---:|
| 120 | 0.999999286201 | 0.999980562189 | 0.0174665107 | 1.148e-07 |
| 240 | 0.999999212540 | 0.999980517691 | 0.0174688518 | 1.215e-07 |
| 480 | 0.999999193043 | 0.999980505865 | 0.0174694351 | 1.239e-07 |

## Full-matrix comparison

- 120 -> 240: raw Frobenius 1.882452e-01; phase-aligned Frobenius 6.210670e-05; max element 4.390875e-05; conditional-phase difference -2.341126e-06 rad
- 240 -> 480: raw Frobenius 4.687503e-02; phase-aligned Frobenius 1.549516e-05; max element 1.095493e-05; conditional-phase difference -5.833101e-07 rad

Second-order Richardson phase estimate: 0.017469629561730086

This is a closed-system model result, not an experimental gate fidelity or hardware release signoff.
