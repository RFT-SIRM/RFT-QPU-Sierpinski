# Stage 9 — bias-shifted gate convergence

Status: closed-system numerical convergence check, not hardware qualification.

Bias offset: -0.0075000 Phi0; absolute bias: 0.259343676252 Phi0.
Static ZZ: -0.000766700 MHz; static A-B detuning: 987.673221499 MHz.
Pump: 987.609221499191 MHz; common pulse duration: 1.081002799581705 us.
Minimum tracked bare overlap: 0.994244823.

| Grid | A→B | B→A | Process overlap | Conditional phase (rad) | Final leakage max | Coupler sampled max |
|---:|---:|---:|---:|---:|---:|---:|
| 120 | 0.999984079634 | 0.999984079207 | 0.999991738189 | 0.0021866839 | 1.064e-08 | 0.005899 |
| 240 | 0.999983338987 | 0.999983338465 | 0.999991365524 | 0.0021939247 | 1.148e-08 | 0.005897 |
| 480 | 0.999983152623 | 0.999983152074 | 0.999991271648 | 0.0021957288 | 1.218e-08 | 0.005897 |

## Full logical matrix convergence

- 120→240: raw Frobenius 1.812766e-01; after local-Z frame alignment 1.297720e-04; max element 9.172621e-05.
- 240→480: raw Frobenius 4.513318e-02; after local-Z frame alignment 3.228429e-05; max element 2.281934e-05.

Richardson conditional phase estimate: 0.002196330137156713

## Limitations

- DC bias shift is projected into the retained Stage-5 local 5-level coupler basis
- common physical duration is enforced across grids
- transient extrema are sampled rather than proven continuous-time extrema
- no measured flux-line transfer function, bandwidth, delay, distortion or crosstalk
- closed-system only; no T1/T2 or thermal bath
- nominal capacitances and SQUID parameters remain assumptions, not layout extraction
