# RFT-QPU-Sierpinski

> **A research architecture for a gauge-covariant fractal SU(2) quantum-processing element.**

[![CI](https://img.shields.io/github/actions/workflow/status/RFT-SIRM/RFT-QPU-Sierpinski/test.yml?branch=main&label=CI&style=flat-square)](https://github.com/RFT-SIRM/RFT-QPU-Sierpinski/actions/workflows/test.yml)
[![Prototype](https://img.shields.io/badge/prototype-v0.1-2563eb?style=flat-square)](engineering/physical_prototype/README.md)
[![Geometry](https://img.shields.io/badge/graph-SG%281%29-4777bd?style=flat-square)](#level-1-transmon-tile)
[![Hardware mapping](https://img.shields.io/badge/mapping-12%20transmons-168f83?style=flat-square)](#level-1-transmon-tile)
[![Status](https://img.shields.io/badge/status-pre--experimental-d97706?style=flat-square)](#research-status)
[![License](https://img.shields.io/badge/license-Business%201.0-303846?style=flat-square)](LICENSE.md)

---

## Navigation

**[Executive Summary](#executive-summary)** · **[Architecture](#architecture)** · **[Level-1 Transmon Tile](#level-1-transmon-tile)** · **[Mathematical Anchor](#mathematical-anchor)** · **[Qubit Passport](#qubit-passport)** · **[Validation](#validation)** · **[IP / Patent](#ip--patent-position)** · **[Repository Map](#repository-map)** · **[Installation](#installation)**

---

## Executive Summary

RFT-QPU-Sierpinski investigates a quantum-processing architecture in which a self-similar Sierpiński-gasket graph carries non-Abelian SU(2) edge transport. The first hardware embodiment now has a reproducible **level-1 numerical prototype** mapped to a proposed superconducting-transmon tile.

The current tile has **6 graph sites, 9 graph edges, 3 non-commuting SU(2) links, 12 transmon modes in the single-excitation model, and 22 effective exchange channels**. Its candidate logical qubit is the lowest two-dimensional spectral subspace of the finite Hamiltonian.

The project keeps three evidence layers separate:

1. **Mathematical anchor.** The companion [Evgeny's Theorem](https://github.com/RFT-SIRM/Evgeny-Theorem) repository documents the fourth spectral-moment identity and its normalized limit.
2. **Numerical prototype.** This repository contains a finite-level solver, projected-control analysis, hardware coefficient exports, two-cell projection, and regression tests.
3. **Physical hardware.** The transmon mapping is a design proposal. No device has been fabricated or measured; complex-Z coupling, multilevel circuit-QED, calibration, noise, leakage, and gate fidelity remain open engineering work.

The intended sequence is mathematical reproducibility → numerical characterization → physical single-cell demonstrator → two-cell entangler → modular scaling.

---

## Architecture

For a graph with vertices `V`, degree operator `D`, and SU(2) edge transports `U_ab`, the research Hamiltonian is represented schematically as

$$
H = D \otimes I_2 - \sum_{(a,b)} |a\rangle\langle b| \otimes U_{ab} + \mathrm{h.c.}
$$

with selected transports

$$
U_{ab}=\exp\left(-i\frac{\theta}{2}\sigma_\alpha\right),
\qquad \alpha\in\{x,y,z\}.
$$

The nominal research point is

$$
\theta = \frac{\pi}{2}.
$$

A candidate logical qubit is a selected two-dimensional low-energy subspace with projector `P`, subject to numerical verification of spectral isolation and control quality. Candidate projected controls are

$$
X_L=P S_xP,\qquad Y_L=P S_yP,\qquad Z_L=P S_zP.
$$

These definitions specify the effective graph model. The transmon realization and any protection or fault-tolerance claim require separate physical validation.

---

## Level-1 Transmon Tile

The first proposed hardware embodiment maps each graph site to a dual-rail pair of transmons. The single-excitation sector contains 12 modeled modes and reproduces the level-1 SU(2) graph Hamiltonian.

<p align="center">
  <img src="engineering/physical_prototype/design/level1_transmon_topology.png" alt="Level-1 Sierpinski graph mapped to six dual-rail transmon sites, with identity, X, Y and Z links" width="760">
</p>

<p align="center"><sub>Proposed topology: 6 graph sites · 9 graph edges · 3 non-commuting SU(2) face links · 12 transmons. This is a design schematic, not a fabricated chip.</sub></p>

| Link class | Graph edges | Effective exchange channels |
|---|---:|---:|
| Identity | 6 | 12 |
| X transport | 1 | 4 |
| Y transport | 1 | 4 |
| Z transport | 1 | 2 |
| **Total** | **9** | **22** |

The active Z link is the present implementation blocker: its required hopping amplitudes are complex, while a single real static coupler cannot reproduce them. A phase-engineered parametric or multi-path implementation, or a revised rotating-frame/frequency plan, must be worked out before tape-out. See [Physical Realization](engineering/physical_prototype/docs/PHYSICAL_REALIZATION.md) and the [hardware risk register](engineering/physical_prototype/docs/RISK_REGISTER.md).

---

## Mathematical Anchor

The companion repository establishes the central fourth-moment result numerically and analytically at the stated mathematical level:

$$
\Delta_m(H^4,\theta)
=-16\left(3^{m-1}+1\right)\sin^2\left(\frac{\theta}{2}\right).
$$

With normalization by `3^(m+1)+3`, the intensive invariant at `θ = π/2` approaches

$$
I_m\left(\frac{\pi}{2}\right)\longrightarrow -\frac{8}{9}.
$$

The current companion repository also documents gauge-invariance checks, vanishing of the first three spectral moments in the relevant defect construction, higher-moment numerical results, and the current Lean 4 formalization boundary. See the [theorem repository](https://github.com/RFT-SIRM/Evgeny-Theorem).

> **Important:** `−8/9` is a normalized fourth spectral-moment invariant. It is **not** an energy gap and must not be presented as one.

---

## Qubit Passport

| Parameter | Research specification |
|---|---|
| Geometry | Sierpiński-gasket graph |
| Internal degree | SU(2) spinor / pseudospin |
| Nominal connection angle | `θ = π/2` |
| Logical dimension | `dim(Q) = 2` candidate subspace |
| Encoding | Selected low-energy subspace `Q = Ran(P)` |
| Logical controls | `P Sx P`, `P Sy P`, `P Sz P` |
| Spectral anchor | `I∞(π/2) = −8/9` |
| Effective-control scale | Level 1: `g_eff = 0.1770433` at vertex 5; level 5 reference: `g_eff ≈ 0.015085`; level-dependent |
| Leakage gap | Must be recomputed for graph refinement, normalization and physical parameter set |
| Experimental status | Not experimentally validated |

### Evidence boundary

The value is **level- and convention-dependent**. The current finite-level study reports `g_eff = 0.1770433` for the level-1 local control at vertex 5, while `g_eff ≈ 0.015085` is the level-5 reference value. They are different finite graphs, not competing estimates of one universal constant.

The computed level-1 leakage gap is `1.3937126931 J`. Neither this gap nor any other device gap follows from `I∞ = −8/9`; the latter is a normalized fourth-moment invariant.

---

## Validation

The numerical prototype now computes the finite-level graph, candidate doublet, leakage separation, projected local controls, hardware channel map and two-cell projected interaction. Physical acceptance still requires:

- two-dimensional logical-subspace isolation;
- reproducible spectral gap to leakage states;
- projected-control linear independence and controllability;
- gate fidelity under calibration uncertainty;
- leakage during single- and two-qubit operations;
- sensitivity to non-gauge perturbations;
- fabrication disorder and parameter spread;
- thermal excitation and relaxation;
- readout fidelity;
- inter-qubit coupling and crosstalk;
- scaling with refinement level and device count.

Gauge covariance of the mathematical spectrum is not equivalent to immunity from arbitrary laboratory noise.

---

## IP / Patent Position

The repository contains a technical disclosure intended to organize the architecture for patent counsel review. It identifies potentially protectable combinations such as:

- self-similar graph connectivity used as a quantum-processing substrate;
- non-Abelian SU(2) edge transport;
- a prescribed connection-angle/axis construction;
- logical encoding into a selected two-dimensional low-energy subspace;
- projected logical controls;
- calibration and validation procedures tied to the spectral construction.

See **[PATENT_SPEC.md](PATENT_SPEC.md)**.

This document is a technical disclosure, **not a legal opinion and not a statement that any claim is patentable**. Patentability depends on jurisdiction, priority date, enablement, written description, novelty, inventive step/non-obviousness, and prior art.

---

## Comparison Framework

See **[COMPARISON.md](COMPARISON.md)** for a factual architecture comparison covering classical accelerators, mainstream superconducting quantum processors, and the proposed RFT-QPU architecture. It intentionally avoids unsupported claims of superiority.

---

## Installation

### Requirements

- Python 3.10+
- NumPy
- pytest for the test suite

### Quick start

```bash
git clone https://github.com/RFT-SIRM/RFT-QPU-Sierpinski.git
cd RFT-QPU-Sierpinski
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python qpu_core.py
pytest -q
```

The top-level `qpu_core.py` is a compact research reference. The full finite-level numerical and hardware-mapping package is `engineering/physical_prototype/`; install it separately using its project instructions.

---

## Engineering Prototype v0.3 research update

The standalone numerical and engineering package is maintained in
[engineering/physical_prototype](engineering/physical_prototype/README.md).

The level-1 topology schematic is shown above; the generated coefficient map contains 22 nonzero effective exchange channels. The current model also includes a two-cell, 24-mode projected interaction.

Reproducibility status: 42 package tests pass in the current local development package; the merged main baseline CI passed. The new qutrit/Floquet screening changes are in PR validation. Numerical values below are model outputs, not measurements:

| Quantity | Numerical result |
|---|---:|
| Level-1 modeled modes / proposed transmon mapping | 12 |
| Ground-doublet splitting divided by J | `1.61 × 10^-15` |
| Gap to the next level divided by J | `1.3937126931` |
| Best local projected-control coefficient | `0.1770433` |
| Two-cell modeled modes / proposed transmon mapping | 24 |
| Projected nonlocal interaction coefficient divided by χ | `0.00783608327` |
| Idealized gate time at assumed χ/(2π) = 10 MHz | `6.38074 μs` |

The near-zero doublet splitting is a floating-point numerical result,
not a formal proof of exact degeneracy. The two-cell gate time is an
idealized projected-model estimate, not a calibrated or measured gate.

This package is not a fabrication-ready design. The resonant complex-Z hopping phase is the immediate pre-tape-out blocker. Multilevel circuit-QED modeling, electromagnetic validation, coupler parasitics, and open-system noise and control analysis also remain outstanding.

These calculations concern the SU(2) RFT-QPU model. They must not be
conflated with the distinct signed-Z2 operator family studied in Phi-Genesis.

## Companion theorem repository

The mathematical reference implementation and Lean 4 formalization are maintained separately:

**[RFT-SIRM / Evgeny-Theorem](https://github.com/RFT-SIRM/Evgeny-Theorem)**

The current public status distinguishes the machine-checked graph infrastructure from the still-open general operator-level Lean proof of `TraceDefectIdentity`. That distinction is intentional and should remain visible in investor and patent materials.

---

## Repository Map

| File | Purpose |
|---|---|
| [PATENT_SPEC.md](PATENT_SPEC.md) | Patent-oriented technical disclosure |
| [COMPARISON.md](COMPARISON.md) | Factual technology comparison |
| [INVESTOR_BRIEF.md](INVESTOR_BRIEF.md) | Investor / partner one-page narrative |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Mathematical-to-transmon architecture and current device mapping |
| [site preview](docs/index.html) | Responsive, self-contained architecture presentation |
| [SITE_DEPLOYMENT.md](docs/SITE_DEPLOYMENT.md) | Publication boundary and deployment prerequisites |
| [VALIDATION_PLAN.md](docs/VALIDATION_PLAN.md) | Updated numerical-to-hardware validation gates |
| [level-1 topology SVG](engineering/physical_prototype/design/level1_transmon_topology.svg) | Source schematic for the 12-transmon demonstrator |
| [DISCLOSURE_BOUNDARY.md](docs/DISCLOSURE_BOUNDARY.md) | What is established vs proposed |
| [qpu_core.py](qpu_core.py) | Minimal numerical core |
| [engineering/physical_prototype/README.md](engineering/physical_prototype/README.md) | Executable numerical and engineering prototype |
| [tests/test_qpu_core.py](tests/test_qpu_core.py) | Core simulator tests |
| [requirements.txt](requirements.txt) | Runtime/test dependencies |
| [CITATION.cff](CITATION.cff) | Citation metadata |
| [LICENSE.md](LICENSE.md) | Business 1.0 proprietary license |

---

## Research Status

**Status: research architecture / pre-experimental.**

No statement in this repository should be read as a claim of demonstrated fault tolerance, universal error correction, arbitrary-noise immunity, commercial fabrication readiness, or experimentally measured qubit performance.

The purpose of this repository is to make the proposed architecture precise enough to be independently simulated, challenged, refined, and eventually tested.


## Nine-tone pump collision screen — 11 November 2026

The isolated 245 MHz phase-conjugate Z link has a reduced four-qutrit process overlap of 0.999609. However, the first-order graph-wide screen of the nine-tone schedule finds a 0 MHz minimum primary resonance margin and 73 primary pump/sideband warnings within 10 MHz across the 22 channel rows. Conditional second/third harmonics and pairwise intermodulation scenarios raise the warning count to 653. These are possible resonances if cross-coupling exists, not measured error probabilities.

The current schedule is **not cleared for simultaneous nine-tone operation**. Reproduce the audit from the engineering package with `PYTHONPATH=src python scripts/run_floquet_audit.py`. See [the detailed audit](engineering/physical_prototype/docs/FLOQUET_COLLISION_AUDIT.md). A redesigned frame assignment, measured 22×22 channel-transfer matrix and explicit data–coupler–data circuit model remain required.
