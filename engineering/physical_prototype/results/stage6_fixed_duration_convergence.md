# Stage 6 — full-gate convergence at a shared physical duration

All time grids use exactly the same physical pulse duration; only the integration step changes.

- Requested duration: 1.062565406772315 us
- Shared actual duration: 1.062567558773707 us
- Common GCD steps per period: 120
- Grids: 120, 240, 480

| Grid | Actual duration (us) | A→B transfer | Process overlap | Conditional phase (rad) |
|---:|---:|---:|---:|---:|
| 120 | 1.062567558773707 | 0.999999766284 | 0.999980795546 | 0.01746968975 |
| 240 | 1.062567558773707 | 0.999999743124 | 0.999980776281 | 0.01747204798 |
| 480 | 1.062567558773707 | 0.999999736342 | 0.999980770807 | 0.01747263555 |

## Full-matrix phase alignment

- 120→240: raw Frobenius 0.1879785792; after independent local-Z/global-phase alignment 3.706200849e-05; max element 2.61943035e-05.
- 240→480: raw Frobenius 0.04680819759; after independent local-Z/global-phase alignment 9.695314515e-06; max element 6.852616953e-06.

## Richardson extrapolation

- transfer_A_to_B: 0.9999997340812004
- transfer_B_to_A: 0.9999997901843466
- conditional_phase_iSWAP_rad: 0.017472831407742116
- projected_process_overlap_after_local_Z: 0.9999807689820858
- average_logical_fidelity_including_leakage: 0.9999846038025929

## Evidence boundary

No experimental or hardware-qualified gate fidelity is claimed.
