# Stage 9 — bias-shifted gate convergence

Status: closed-system numerical convergence check, not hardware qualification.

Bias offset: -0.0075000 Phi0; absolute bias: 0.259343676252 Phi0.
Static ZZ: -0.000766700 MHz; static A-B detuning: 987.673221499 MHz.
Pump: 987.610221499191 MHz; common pulse duration: 1.081001705017497 us.
Minimum tracked bare overlap: 0.994244823.

| Grid | A→B | B→A | Process overlap | Conditional phase (rad) | Final leakage max | Coupler sampled max |
|---:|---:|---:|---:|---:|---:|---:|
| 120 | 0.999962532445 | 0.999962532019 | 0.999980964563 | 0.0021867027 | 1.050e-08 | 0.005899 |
| 240 | 0.999961399918 | 0.999961399397 | 0.999980396068 | 0.0021939435 | 1.078e-08 | 0.005897 |
| 480 | 0.999961115357 | 0.999961114808 | 0.999980252999 | 0.0021957476 | 1.218e-08 | 0.005897 |

## Full logical matrix convergence

- 120→240: raw Frobenius 1.812760e-01; after local-Z frame alignment 1.299232e-04; max element 9.183220e-05.
- 240→480: raw Frobenius 4.513304e-02; after local-Z frame alignment 3.231713e-05; max element 2.284232e-05.

Richardson conditional phase estimate: 0.0021963489985728454

## Limitations

- DC bias shift is projected into the retained Stage-5 local 5-level coupler basis
- common physical duration is enforced across grids
- transient extrema are sampled rather than proven continuous-time extrema
- no measured flux-line transfer function, bandwidth, delay, distortion or crosstalk
- closed-system only; no T1/T2 or thermal bath
- nominal capacitances and SQUID parameters remain assumptions, not layout extraction
