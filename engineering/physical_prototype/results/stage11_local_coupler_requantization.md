# Stage 11A — local SQUID-coupler re-quantization

- Base flux: `0.266843676259890 Phi0`
- Bias offset: `-0.00750000 Phi0`
- Re-quantized flux: `0.259343676259890 Phi0`
- Charge cutoffs: `[8, 10, 12]`
- Retained local levels: `[3, 4, 5]`

| Cutoff | Levels | old f01 (MHz) | new f01 (MHz) | Δf01 (MHz) | min state overlap | min subspace σ | Δ|n01| |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 3 | 5007.500000001 | 5075.910813298 | +68.410813297 | 0.999782337 | 0.999904150 | +7.038751305e-03 |
| 8 | 4 | 5007.500000001 | 5075.910813298 | +68.410813297 | 0.999606393 | 0.999838673 | +7.038751305e-03 |
| 8 | 5 | 5007.500000001 | 5075.910813298 | +68.410813297 | 0.998968243 | 0.999569156 | +7.038751305e-03 |
| 10 | 3 | 5007.499999931 | 5075.910813204 | +68.410813273 | 0.999782337 | 0.999904150 | +7.038751309e-03 |
| 10 | 4 | 5007.499999931 | 5075.910813204 | +68.410813273 | 0.999606393 | 0.999838673 | +7.038751309e-03 |
| 10 | 5 | 5007.499999931 | 5075.910813204 | +68.410813273 | 0.998968242 | 0.999569156 | +7.038751309e-03 |
| 12 | 3 | 5007.499999931 | 5075.910813204 | +68.410813273 | 0.999782337 | 0.999904150 | +7.038751309e-03 |
| 12 | 4 | 5007.499999931 | 5075.910813204 | +68.410813273 | 0.999606393 | 0.999838673 | +7.038751309e-03 |
| 12 | 5 | 5007.499999931 | 5075.910813204 | +68.410813273 | 0.998968242 | 0.999569156 | +7.038751309e-03 |

## Scope and limitations
Local SQUID-coupler charge-basis diagonalization only. The result does not yet rebuild the full three-mode driven Hamiltonian, recalculate the complete logical gate, or establish hardware readiness. Capacitances and Josephson parameters remain the declared Stage-3 assumptions.

The aligned operator matrices and overlap matrices are in the companion NPZ. This audit is a prerequisite to, not a substitute for, rebuilding and converging the full driven three-mode logical gate in the new basis.
