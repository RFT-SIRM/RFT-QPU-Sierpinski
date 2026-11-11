# Stage 11B — local pulse-retune record

**Date recorded in repository:** 11 November 2026  
**Evidence class:** local closed-system numerical run reported in the root README  
**Status:** useful engineering result; raw fine-retune JSON/NPZ files are not tracked in this repository.

This note preserves the local Stage 11B retuning values from the repository's README update. It deliberately does not represent the missing local output files as repository artifacts.

## Selected operating point

The local search was performed after the full A–coupler–B model had been rebuilt in the re-quantized shifted-flux coupler basis. The sequence was a bias × pump-frequency screen followed by a local amplitude × duration screen.

| Parameter | Selected value |
|---|---:|
| DC bias | 0.25884589447013934 Φ₀ |
| Pump frequency | 987.6171621707836 MHz |
| Flux amplitude | 0.0199946062 Φ₀ |
| Requested duration | 1.081140796 μs |
| Raised-cosine ramp | 8 pump periods |

## Five-level result at 480 steps per period

| Metric | Reported result |
|---|---:|
| Product Hilbert-space dimension | 125 |
| Projected process overlap after local-Z fit | 0.9999999793763371 |
| Average logical-state fidelity including leakage | 0.9999999803654352 |
| A→B transfer probability | 0.9999999973549074 |
| B→A transfer probability | 0.999999992602828 |
| Conditional iSWAP phase | 0.00027739757232 rad |
| Final norm error | 1.31284649818042×10⁻⁹ |
| Maximum sampled logical leakage | 3.3115929888805073×10⁻⁴ |
| Maximum sampled coupler-excited population | 6.089711727433299×10⁻³ |

The reported transfer probabilities, process overlap and average logical-state fidelity are projected closed-system metrics. They are not measured hardware fidelity. The leakage and coupler population are sampled along the simulated pulse; they are not continuous-time bounds.

## Retained-level and charge-cutoff checks recorded in the README

- At the same operating point and 480 steps per period, the six-level (216-dimensional) projected process overlap after local-Z fitting was 0.999999967757.
- The five-/six-level phase-aligned matrix Frobenius difference at 480 steps per period was 1.8981859×10⁻⁴.
- The seven-level result is only a 120-step-per-period spot check. Its phase-aligned matrix difference from the six-level result at that grid was 2.3211679×10⁻⁵. Seven-level 240/480 propagation remains open.
- In the five-retained-level driven charge-cutoff screen, full logical-matrix difference relative to cutoff 10 was 8.15265699×10⁻⁸ at cutoff 8 and 8.77748965×10⁻⁸ at cutoff 12.
- The three-/four-retained-level variants differed by approximately 9.79443104×10⁻⁴ and 9.23700332×10⁻⁴, respectively.

These checks support the local five-level result but do not establish full retained-level convergence or a worst-case robustness envelope.

## SHA-256 fingerprints reported by the local run

| Local artifact | SHA-256 |
|---|---|
| FineRobustness report JSON | 46ed497a3c244e802182ac56c48f3652588d0ecc913ba16e22327a4af5625cac |
| FineRobustness matrices NPZ | 1ef4fa45bfb76727d98f561b58ba1693a9593a3819ce3ac7d043b7c35a274942 |
| LocalPulseRetune report JSON | b0fa114e4e4d7de9d95cd2441e6de25093543a8d2b66d401226d296427512c21 |
| LocalPulseRetune matrices NPZ | e3c250f214ba2ac77cdd9aa208cf09f036c4e9e7deb3d262d3ef2b7b822cfbe4 |

The fingerprints identify files that were present in the user's local run folders. The raw files themselves were not present in the GitHub workspace during the README update and are not represented as tracked repository files here. A hash cannot reconstruct an absent report or matrix archive.

## Required archival close-out

- [ ] Add the original FineRobustness report JSON and matrices NPZ.
- [ ] Add the original LocalPulseRetune report JSON and matrices NPZ.
- [ ] Preserve each original manifest and verify the recorded SHA-256.
- [ ] Add the exact command line, environment and source commit used for each run.
- [ ] Add a deterministic runner/configuration that regenerates the selected point.
- [ ] Complete seven-level 240/480 propagation and full matrix comparisons.
- [ ] Record uncertainty sweeps rather than only the selected nominal point.

Until those steps are complete, refer to this as a reported local retune, not a fully archived and independently reproducible repository result.
