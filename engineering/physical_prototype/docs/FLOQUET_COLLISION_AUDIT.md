# Level-1 nine-tone Floquet collision audit

**Status: first-order screening run; current frame plan fails its resonance guard.**  
**Run date:** 11 November 2026  
**Command:** `PYTHONPATH=src python scripts/run_floquet_audit.py`

The input is the level-1 coefficient export: six graph sites, nine edges and 22 nonzero effective exchange channels. The screen includes assumed data-transmon Duffing anharmonicities (-250 MHz up, -245 MHz down), both rotating-frame sidebands, N=1 exchange and N=2 transitions.

For a victim edge with signed local-frame difference Δf, a source component f creates sidebands |Δf ± f|. These are compared with:
- N=1 exchange: |Δonsite|;
- |11> ↔ |20>: |Δonsite + αa|;
- |11> ↔ |02>: |Δonsite − αb|;
- |20> ↔ |02>: |2Δonsite + αa − αb|.

## Current result

Offsets: (0, 350, 270, 465, 515, 655) MHz. Pump references: 50, 80, 115, 140, 165, 245, 270, 350, 385 MHz.

| Screen | Checks | Warnings ≤10 MHz | Minimum margin |
|---|---:|---:|---:|
| Primary tones | 1,556 | 73 | **0 MHz** |
| Primary + conditional harmonics/intermodulation | 17,396 | 653 | **0 MHz** |

Example exact candidate: the 80 MHz e002 pump can, if it leaks into the e000 path, produce a 270 MHz component in the e000 rotating frame. This matches the assumed q00_up/q01_up |11>→|20> transition. This is a resonance candidate, not a measured leakage event.

Harmonic and sum/difference intermodulation products are conditional scenarios; their actual amplitudes depend on the physical coupler and drive transfer functions. The audit does not predict error probability and is not a full Floquet/Sambe solve.

**Decision: do not activate all nine tones simultaneously using this assignment.** Redesign the six frame offsets, measure/extract the complex 22×22 pump-channel transfer matrix and coupler response, then run full multitone circuit/Floquet and open-system validation. The 245 MHz phase-conjugate Z result remains an isolated-link reduced-model checkpoint only.
