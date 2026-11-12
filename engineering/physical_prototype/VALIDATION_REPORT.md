# Validation record — engineering model v0.4-rc1

**Date:** 12 November 2026  
**Channel:** public numerical-model record; not hardware qualification  
**Project author attribution:** Evgeny Zaprudnov

## Recorded software checks

Historical local preparation recorded:

    python -m compileall -q engineering/physical_prototype/src engineering/physical_prototype/scripts engineering/physical_prototype/tests
    python -m pytest -q tests engineering/physical_prototype/tests

Result: **75 passed in 1.33 s** on Python 3.14.2.

The merged Stage 11B PR #5 has a successful GitHub Actions run #23 (run ID 42976933542) on reviewed head 7ce294c54de0c0b046a4503aede9db714ca747ac. The subsequent public-release baseline commit db606c428183aab0b637ce449d08b604d260e0e4 passed GitHub Actions run #29 on Python 3.11: **78 tests passed**, and the level-1 device calculation, two-cell projected interaction, and graph-wide qutrit/Floquet collision audit all completed successfully. Run #29 is a model/software check, not physical hardware validation.

## Stage 10 fixed-basis reference

At 480 steps per pump period:

- Bias: 0.259343676252 Φ₀.
- Pump: 987.609221499 MHz.
- Amplitude: 0.020000 Φ₀.
- Common duration: 1.081002799582 μs.
- A→B / B→A: 0.999983152623 / 0.999983152074.
- Projected process overlap after local-Z fit: 0.999991271648.
- Conditional iSWAP phase: 0.0021957288 rad.

Stages 5–10 use the retained Stage-5 local coupler basis.

## Stage 11A local SQUID re-quantization

At charge cutoff 12 with five retained local levels, the coupler f01 changes from 5007.500000 MHz to 5075.910813 MHz, a shift of +68.410813 MHz. The minimum matched-state overlap probability is 0.9989682 and the minimum retained-subspace singular value is 0.9995692. The local study spans charge cutoffs 8/10/12 and retained levels 3/4/5.

## Stage 11B initial re-quantized full-gate baseline

The A–coupler–B product Hamiltonian was rebuilt in the shifted local SQUID eigenbasis with charge cutoff 10 and five retained levels per mode (dimension 125). The unchanged Stage-10 pulse was propagated on 120/240/480 grids. At 480 steps per period: A→B 0.999984205861, B→A 0.999984205140, projected process overlap after local-Z fitting 0.999991791082, conditional phase 0.002216577957 rad. Full complex logical matrices and diagnostics are tracked in the Stage 11B JSON and NPZ archive.

## Stage 11B local retune

The root README records a later selected local point:
- bias 0.25884589447013934 Φ₀;
- pump 987.6171621707836 MHz;
- amplitude 0.0199946062 Φ₀;
- requested duration 1.081140796 μs;
- 8-period raised-cosine ramp.

At five levels and 480 steps per period, the reported projected process overlap after local-Z fit is 0.9999999793763371 and average logical-state fidelity including leakage is 0.9999999803654352. The six-level 480-grid process overlap is 0.999999967757. The seven-level model has only a 120-grid spot check.

The raw fine-retune JSON/NPZ outputs are not tracked in the repository. SHA-256 fingerprints and numerical limits are recorded in docs/STAGE11B_LOCAL_RETUNE_NOTE.md. These reported values should not be treated as a fully reproducible archived run until the files and a reproduction configuration are added.

## Physical evidence not established

- No fabricated or measured chip.
- No measured capacitance matrix or layout-extracted parasitics.
- No complete seven-level 240/480 temporal convergence or fully matched retained-level convergence for the retuned point.
- No robust worst-case pulse-tolerance envelope.
- No measured flux-line transfer function, pump crosstalk, phase-noise or distortion budget.
- No T1/T2, thermal-bath or open-system gate fidelity.
- No fabrication-yield, packaging, readout or independent hardware qualification.
- No cleared simultaneous nine-tone graph-wide schedule; the existing first-order screen reports 73 primary and 653 conditional warnings.

A passing software suite establishes reproducibility of the encoded numerical model only. It does not establish hardware readiness, tape-out readiness or experimental gate performance.
