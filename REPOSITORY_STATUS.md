# Repository status — public-release preparation

**Review date:** 12 November 2026  
**Repository:** RFT-SIRM/RFT-QPU-Sierpinski  
**Default branch:** main  
**Baseline before this documentation update:** 89bdb6d9b02989bdbe01f643d1156419dbbb056b  
**Engineering checkpoint:** v0.4-rc1 numerical-model pre-release  
**Project author attribution:** Evgeny Zaprudnov

## Publication and licence

GitHub repository metadata was rechecked on 12 November 2026 and reports this repository as **public**. The first-public timestamp is not exposed by the repository metadata available in this audit; see the disclosure log for the date and verified public baseline.

The source licence is BUSL-1.1 with no Additional Use Grant. It permits non-production use, copying, modification and redistribution under its terms. Production use requires a separate written commercial agreement. The Change Date is 12 November 2030, or the fourth anniversary of first public distribution of the relevant version if earlier; the Change License is GPL-2.0-only.

A separate, perpetual and irrevocable (subject to defensive termination) patent grant accompanies BUSL-1.1. It only covers claims the Licensor actually owns or legally controls and that are necessarily infringed by the Licensor's contributions, and it is coextensive with the source-licence scope. This grant is a licence to recipients, not patent protection for the Licensor; qualifying future claims may be pre-licensed non-exclusively. See PATENTS.md before making any patent or exclusivity assumptions.

## Engineering scope

The repository contains the finite Sierpiński graph family and SU(2) Hamiltonian; level-1 proposed transmon mapping; hardware coefficient and channel tables; two-cell projected-interaction study; graph-wide pump-collision audit; three-mode SQUID-coupler model; Stages 1–11B scripts, tests, reports and selected numerical archives.

The level-1 mapping contains 6 graph sites, 9 graph edges, 3 selected non-commuting X/Y/Z links, 12 transmon modes and 22 effective exchange channels. It is a proposed implementation, not a fabricated chip or foundry-ready netlist.

## Current evidence

| Area | Evidence in repository | Status |
|---|---|---|
| SG graph family | Finite levels 1–5, source and regression tests | Implemented numerical model |
| SU(2) graph Hamiltonian | Hermiticity, covariance and symmetry checks | Implemented numerical model |
| Candidate low-energy doublet | Ideal finite-model spectral result near floating-point tolerance | Candidate subspace, not a manufactured-device result |
| Level-1 projected controls | Local and global projected-control matrices | Ideal-model numerical result |
| Level-1 transmon map | 12 modes and 22 effective exchange channels | Proposed hardware mapping |
| Two-cell interaction | Static projected coefficient 0.00783608327 χ | Numerical projection, not an executed entangling gate |
| Nine-tone plan | 73 primary and 653 conditional warnings; zero minimum primary margin | Not cleared for simultaneous operation |
| Stage 11B baseline | Tracked three-mode A–coupler–B JSON/NPZ and 120/240/480 time-grid comparisons | Closed-system numerical baseline |
| Stage 11B local retune | Five-level 480-grid metrics; six-level 480-grid comparison; seven-level 120-grid spot check | Reported local result; raw retune JSON/NPZ not tracked |
| Fabricated/measured hardware | No chip, measured T1/T2, measured gate fidelity or independent hardware qualification recorded | Not demonstrated |

## Stage 11B local retune

The reported local point is:
- DC bias 0.25884589447013934 Φ₀;
- pump 987.6171621707836 MHz;
- amplitude 0.0199946062 Φ₀;
- requested duration 1.081140796 μs;
- raised-cosine ramp of 8 pump periods.

At five retained levels and 480 steps per period, the reported projected process overlap after local-Z fitting is 0.9999999793763371 and average logical-state fidelity including leakage is 0.9999999803654352. The six-level 480-grid overlap is 0.999999967757. The raw fine-retune JSON/NPZ files are not tracked; their hashes do not reproduce the missing files. Seven-level 240/480 propagation remains open.

## Software validation record

- Historical local preparation: Python 3.14.2, 75 tests passed.
- Merged Stage 11B PR #5: GitHub Actions run #23 succeeded on its reviewed PR head.
- Previous documentation PR #6 and its post-merge workflow completed successfully.
- Public-release baseline db606c428183aab0b637ce449d08b604d260e0e4 passed GitHub Actions run #29: 78 tests plus the level-1, two-cell and graph-wide qutrit/Floquet reproduction steps succeeded.

A passing software suite validates the encoded computation and tests only. It does not establish physical feasibility, yield, hardware fidelity, fault tolerance or tape-out readiness.

## Open engineering gates

1. Archive the raw Stage 11B local-retune JSON/NPZ, original manifests, exact commands and source commit.
2. Complete seven-level 240/480 temporal propagation and phase-aligned matrix comparisons.
3. Extend retained-level and charge-cutoff convergence for the retuned gate.
4. Produce pulse-tolerance maps and uncertainty budgets.
5. Resolve the resonant complex-Z link using a concrete physical phase-engineered circuit.
6. Redesign and validate the nine-tone frequency/frame plan.
7. Add flux-line transfer, delay, distortion, pump-phase-noise and crosstalk models.
8. Add open-system T1/T2, thermal, relaxation, dephasing, leakage and spectator models.
9. Replace assumed circuit parameters with layout extraction and independent EM/circuit-QED review.
10. Fabricate and characterize the one-cell and two-cell demonstrators before making hardware or protection claims.

## Related documents

- [README](README.md)
- [LICENSE](LICENSE)
- [Supplemental patent grant](PATENTS.md)
- [IP and licensing](IP_AND_LICENSING.md)
- [Public technical disclosure](PATENT_SPEC.md)
- [Evidence boundary](docs/DISCLOSURE_BOUNDARY.md)
- [Validation plan](docs/VALIDATION_PLAN.md)
- [Public branch map](docs/BRANCH_STATUS.md)
- [Engineering package](engineering/physical_prototype/README.md)
