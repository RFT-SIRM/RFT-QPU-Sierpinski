# Repository status — reviewed 11 November 2026

## Repository identity and handling

- Repository: RFT-SIRM/RFT-QPU-Sierpinski.
- Visibility verified through repository metadata: **private**.
- Default branch: main.
- Main commit at review start: 39c55368d3b3f76ccf0e5116ced0bb0d66dcf9fd.
- Engineering checkpoint: closed/internal software and model pre-release candidate v0.4-rc1.
- Project author attribution requested for project materials: **Evgeny Zaprudnov**.
- The documentation review is being prepared on a separate private branch. No change to main or repository visibility is part of this status record.

## What is in this repository

The repository contains the graph model, SU(2) Hamiltonian, finite-level numerical package, proposed level-1 transmon mapping, generated hardware coefficient tables, two-cell projected-interaction study, graph-wide pump-collision screen, circuit-derived three-mode coupler model, scripts, tests, reports and numerical archives.

The current repository covers Stages 1–11B. Stage 11B has two distinct evidence records:

1. The initial re-quantized three-mode baseline is archived in tracked JSON and NPZ files and has 120/240/480 temporal-grid comparisons.
2. A later local pulse retune is reported in the root README with selected parameters, 480-grid metrics, five-/six-level checks and SHA-256 fingerprints. Its raw fine-retune JSON/NPZ files are not tracked in the repository.

## Current evidence status

| Area | Repository evidence | Status |
|---|---|---|
| SG graph family and finite-level counts | Source, tests and reports for levels 1–5 | Implemented numerical model |
| SU(2) graph Hamiltonian | Source and Hermiticity/symmetry regression tests | Implemented numerical model |
| Candidate lowest doublet | Floating-point spectral results | Candidate subspace; exact manufactured degeneracy not claimed |
| Level-1 projected controls | Local and global control matrices; local g_eff = 0.1770433 at vertex 5 | Ideal-model numerical result |
| Level-1 device map | 12 transmon modes, 22 effective exchange channels | Proposed mapping; not a foundry netlist |
| Two-cell interaction | Static projected coefficient 0.00783608327 χ | Numerical projection; no physical entangler |
| Nine-tone frequency allocation | 73 primary warnings and 653 conditional warnings; zero minimum margin | Not cleared for simultaneous operation |
| Stage 11A | Local SQUID re-quantization at shifted bias, cutoffs 8/10/12 and retained levels 3/4/5 | Local audit recorded |
| Stage 11B baseline | Rebuilt A–coupler–B Hamiltonian; tracked 120/240/480 baseline matrices | Completed nominal closed-system baseline |
| Stage 11B local retune | 480-grid five-level result; six-level 480-grid cross-check; seven-level 120-grid spot check | Reported local result; raw retune artifacts not tracked |
| Physical chip, gate and noise | No measured chip, T1/T2, measured gate fidelity, open-system results or layout extraction | Not demonstrated |

## Stage 11B selected local point

The local retune values reported in the repository are:

- DC bias: 0.25884589447013934 Φ₀.
- Pump: 987.6171621707836 MHz.
- Flux amplitude: 0.0199946062 Φ₀.
- Requested duration: 1.081140796 μs.
- Raised-cosine ramp: 8 pump periods.
- Five-level 480-grid projected process overlap after local-Z fitting: 0.9999999793763371.
- Six-level 480-grid projected process overlap: 0.999999967757.

The local results are useful engineering evidence, but the raw JSON/NPZ hashes and matrices are not a substitute for the files themselves. See [Stage 11B local retune note](engineering/physical_prototype/docs/STAGE11B_LOCAL_RETUNE_NOTE.md).

## Numerical validation record

- Historical local preparation: Python 3.14.2, 75 tests passed in 1.33 s.
- Merged Stage 11B PR #5: GitHub Actions run #23 completed successfully on head 7ce294c54de0c0b046a4503aede9db714ca747ac.
- The main commit at the start of this documentation review is 39c55368d3b3f76ccf0e5116ced0bb0d66dcf9fd.
- The status checks API did not return separate status entries for the main commit at review time. No claim is made here that a documentation-branch CI run has passed.

A passing software suite validates the encoded computation and tests only. It does not establish physical feasibility, device yield, hardware fidelity, fault tolerance or tape-out readiness.

## Open engineering gates

1. Archive the original Stage 11B retune JSON/NPZ outputs and provide a runner configuration that reproduces the selected point.
2. Complete seven-level 240/480 temporal propagation and matched phase-aligned matrix comparisons.
3. Extend full driven-gate convergence across charge cutoffs and retained levels.
4. Convert deterministic local pulse searches into parameter-tolerance maps and uncertainty budgets.
5. Resolve the resonant complex-Z link with a concrete phase-engineered circuit.
6. Redesign and validate the nine-tone frequency/frame allocation; the current screen is not cleared.
7. Add measured/target flux-line transfer, distortion, delay, pump phase noise and crosstalk.
8. Add open-system T1/T2, thermal, relaxation, dephasing, leakage and spectator models.
9. Replace assumed capacitances/Josephson parameters with layout-extracted values and independent EM/circuit-QED review.
10. Fabricate and characterize the one-cell and two-cell demonstrations before making hardware or protection claims.

## IP and legal-document status

This repository records a project-author attribution to Evgeny Zaprudnov. It does not, on its own, establish all inventors, rights holders, employment/contractual assignments, contributor assignments or ownership of improvements.

No patent application number, filing date, patent office, granted patent, signed NDA register or commercial licence is recorded in the repository at this review point. These are repository observations, not statements that no off-repository document exists. The project should remain private while filing strategy, disclosure chronology and chain of title are checked.

See [PATENT_SPEC.md](PATENT_SPEC.md), [IP_AND_LICENSING.md](IP_AND_LICENSING.md), [LICENSE.md](LICENSE.md) and [Disclosure log](docs/DISCLOSURE_LOG_TEMPLATE.md).
