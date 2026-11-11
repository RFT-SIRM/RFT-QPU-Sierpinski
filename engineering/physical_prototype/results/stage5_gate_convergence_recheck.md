# Stage 5 — full logical-matrix convergence

This is a reproducible closed-system calculation, not a hardware qualification.

- Pump: 987.513679799316 MHz
- Flux amplitude: 0.02000000 Phi0
- Requested duration: 1.062565406772 us
- Time grids: 120, 240, 480 steps per pump period

| Grid | A→B transfer | Process overlap after local Z | Conditional phase (rad) | Logical unitarity defect |
|---:|---:|---:|---:|---:|
| 120 | 0.999999766284 | 0.999980795546 | 0.01746968975 | 1.473e-07 |
| 240 | 0.999999742240 | 0.999980775989 | 0.01747197834 | 1.566e-07 |
| 480 | 0.999999735942 | 0.999980770682 | 0.01747260074 | 1.600e-07 |

## Full matrix comparison

- 120→240: raw Frobenius `0.4900294155`, after independent local-Z/global phase alignment `3.856069279e-05`, max element `2.725589274e-05`.
- 240→480: raw Frobenius `0.1276538556`, after independent local-Z/global phase alignment `8.849699759e-06`, max element `6.253947508e-06`.

## Richardson estimates

- transfer_A_to_B: 0.9999997338432814
- transfer_B_to_A: 0.9999997898248136
- conditional_phase_iSWAP_rad: 0.017472808200253445
- projected_process_overlap_after_local_Z: 0.9999807689133071
- average_logical_fidelity_including_leakage: 0.9999846037466962

## Evidence boundary

No experimental gate fidelity is claimed. The source circuit remains a nominal assumption set. Open-system, flux-line, calibration, fabrication and spectator-channel effects remain outstanding.
