# Closed engineering pre-release candidate v0.4-rc1

Date: 2026-11-11
Base commit: `d9b374c1dbd7e24050a33b13acf21f57858ff775`

## Release intent

This is a closed/internal, reproducible engineering-software checkpoint that consolidates the Stage 1–11A research work. It is **not** a fabrication release, foundry package, tape-out authorization, or experimental hardware claim.

## Current best converged full-gate candidate

Stage 10, still evaluated in the Stage-5 fixed local coupler basis:

- DC flux: `0.259343676252320 Phi0`
- Pump frequency: `987.609221499191 MHz`
- Pump offset: `-64.000000 kHz`
- Flux amplitude: `0.02000000 Phi0`
- Common duration: `1.081002799581705 us`
- 480-grid A→B / B→A: `0.999983152623462` / `0.999983152073742`
- 480-grid projected process overlap after local-Z fitting: `0.999991271647941`
- 480-grid conditional phase: `0.002195728776 rad`

These are closed-system projected metrics, not experimental gate fidelity.

## Stage 11A status

At charge cutoff 12 with five retained local levels, the coupler f01 changes from 5007.500000 MHz to 5075.910813 MHz (Δ +68.410813 MHz); the minimum matched-state overlap probability is 0.9989682 and the minimum retained-subspace singular value is 0.9995692.

Stage 11A is a local coupler basis audit. It is not a full driven-gate rebuild. The Stage 10 gate metrics continue to use the Stage-5 fixed local coupler basis.

## Validation

- Local interpreter: `Python 3.14.2`.
- Local full test suite: **75 passed in 1.33s**.
- Full JSON and NPZ artifact integrity checks are run by the release-preparation procedure.
- The pull-request GitHub Actions run on Python 3.11 must pass before merging.

## Remaining engineering gates

1. Stage 11B complete three-mode Hamiltonian and driven-gate rebuild in the re-quantized basis.
2. Robust optimization using the rebuilt model.
3. Flux-line transfer and pump/crosstalk/noise characterization.
4. Open-system T1/T2 and thermal modeling.
5. Layout extraction, EM/circuit-QED review and fabrication tolerances.
6. Graph-wide nine-tone collision resolution (current audit: 73 primary and 653 conditional warnings).
7. Independent hardware review before any fabrication decision.

## Release decision

Accept as **closed/internal engineering software pre-release candidate v0.4-rc1**, subject to green CI. Do not label it fabrication-ready or experimentally validated.
