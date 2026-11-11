# Pre-release validation record — v0.4-rc1

Date: 2026-11-11
Channel: closed/internal engineering pre-release candidate
Base commit: `d9b374c1dbd7e24050a33b13acf21f57858ff775`
Local interpreter: `Python 3.14.2`

## Executed local checks

Command:

```bash
python -m compileall -q engineering/physical_prototype/src engineering/physical_prototype/scripts engineering/physical_prototype/tests
python -m pytest -q tests engineering/physical_prototype/tests
```

Recorded test result during release-candidate preparation: **75 passed in 1.33s**.

The GitHub Actions pull-request run (repository Python 3.11 workflow) is a separate mandatory release check; it must be green before merging.

## Stage 10 converged candidate

Parameters:

- DC flux: `0.259343676252320 Phi0`
- Pump frequency: `987.609221499191 MHz`
- Pump offset from shifted static detuning: `-64.000000 kHz`
- Flux amplitude: `0.02000000 Phi0`
- Common duration: `1.081002799581705 us`
- Ramp periods: `8.0`

At 480 steps/period:

- A→B: `0.999983152623462`
- B→A: `0.999983152073742`
- Projected process overlap after local-Z fitting: `0.999991271647941`
- Conditional iSWAP phase: `0.002195728776 rad`
- Richardson phase estimate: `0.002196330137 rad`

These are closed-system model metrics, not measured gate fidelity.

## Stage 11A local coupler requantization

At charge cutoff 12 with five retained local levels, the coupler f01 changes from 5007.500000 MHz to 5075.910813 MHz (Δ +68.410813 MHz); the minimum matched-state overlap probability is 0.9989682 and the minimum retained-subspace singular value is 0.9995692.

Truncations evaluated: charge cutoffs `[8, 10, 12]`, retained levels `[3, 4, 5]`. The report archives matched eigenstate/operator data and overlap matrices. This stage re-quantizes the **local coupler only**; it does not rebuild or reconverge the full three-mode driven gate.

## Included evidence

- Stage 1–4 circuit-derived coupler source, tests, reports and checkpoint from the merged baseline.
- Stage 5–10 source, scripts, tests, convergence reports, sweeps and complex logical matrices.
- Stage 11A local coupler re-quantization source, tests, report, CSV and NPZ matrices.
- Updated pre-release scope, validation gates and risk register.

## Not established

- No fabricated or measured chip.
- No measured capacitance matrix or extracted layout parasitics.
- No fully rebuilt Stage 11B gate in the new coupler basis.
- No measured flux-line transfer function, pump crosstalk or phase-noise budget.
- No T1/T2, thermal-bath or open-system gate fidelity.
- No fabrication yield/disorder qualification.
- The nine-tone graph-wide schedule remains uncleared; current screen reports 73 primary and 653 conditional warnings.

A green software suite establishes reproducibility of the encoded numerical model only. It does not establish hardware readiness, tape-out readiness or experimental gate performance.
