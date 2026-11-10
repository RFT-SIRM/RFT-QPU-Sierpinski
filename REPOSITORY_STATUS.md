# Repository Status

## Scope

RFT-QPU-Sierpinski is the proposed architecture repository. The companion `Evgeny-Theorem` repository contains the mathematical reference work and Lean 4 formalization.

## Current evidence boundary

- Fourth spectral-moment result: established in the companion project and documented with analytic/numerical evidence.
- Gauge spectral invariance: numerically validated in the companion project.
- Lean 4 graph infrastructure: machine-checked and computable in the current public repository.
- General operator-level Lean proof of `TraceDefectIdentity`: still identified as open in the current public README; do not advertise it as fully machine-checked.
- Candidate qubit encoding and projected controls: architecture under numerical investigation.
- Physical QPU: not experimentally validated.

## Engineering prototype v0.1

- Standalone package: `engineering/physical_prototype/`.
- Local test suite: 20 tests passed on 10 November 2026.
- Level-1 model: 12 modeled modes in the proposed transmon mapping;
  leakage gap `1.3937126931 J`; best local projected-control coefficient
  `g_eff = 0.1770433`.
- Two-cell projection: 24 modeled modes; projected interaction coefficient
  `0.00783608327 χ`; idealized gate-time estimate `6.38074 μs` at the
  assumed `χ/(2π) = 10 MHz`.
- The doublet splitting is at floating-point roundoff scale, not a proof
  of exact degeneracy. The gate-time estimate is not a measured result.
- Complex-Z coupler implementation, multilevel circuit-QED, electromagnetic
  validation, and open-system noise modeling remain open engineering gates.
- The SU(2) RFT-QPU model is distinct from the signed-Z2 Phi-Genesis model.
