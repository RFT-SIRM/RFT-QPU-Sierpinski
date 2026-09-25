# RFT-QPU-Sierpinski

> **A research architecture for a gauge-covariant fractal SU(2) quantum-processing element.**

[![Website](https://img.shields.io/badge/website-live%20demo-ef4444?style=for-the-badge)](https://rft-sirm.github.io/RFT-QPU-Sierpinski/)
[![Research Status](https://img.shields.io/badge/status-research%20prototype-111827?style=for-the-badge)](#research-status)
[![Geometry](https://img.shields.io/badge/geometry-Sierpi%C5%84ski%20gasket-2563eb?style=for-the-badge)](#architecture)
[![Internal Degree](https://img.shields.io/badge/internal%20degree-SU%282%29-7c3aed?style=for-the-badge)](#architecture)
[![Anchor](https://img.shields.io/badge/anchor-I%E2%88%9E%20%3D%20%E2%88%928%2F9-059669?style=for-the-badge)](#mathematical-anchor)
[![Lean 4](https://img.shields.io/badge/Lean%204-machine--checked%20graph%20layer-0891b2?style=for-the-badge)](https://github.com/RFT-SIRM/Evgeny-Theorem/tree/main/formalization)
[![License](https://img.shields.io/badge/license-Business%201.0-black?style=for-the-badge)](LICENSE.md)

---

## Navigation

**[Executive Summary](#executive-summary)** · **[Architecture](#architecture)** · **[Mathematical Anchor](#mathematical-anchor)** · **[Qubit Passport](#qubit-passport)** · **[Validation](#validation)** · **[IP / Patent](#ip--patent-position)** · **[Repository Map](#repository-map)** · **[Installation](#installation)**

---

## Executive Summary

RFT-QPU-Sierpinski is a proposed quantum-processing architecture built around a self-similar Sierpiński-gasket connectivity structure carrying non-Abelian SU(2) edge transport.

The project is deliberately split into three evidence layers:

1. **Established mathematical anchor.** The companion [Evgeny's Theorem](https://github.com/RFT-SIRM/Evgeny-Theorem) repository reports an exact fourth spectral-moment defect and a normalized asymptotic invariant.
2. **Qubit architecture.** This repository defines a candidate two-dimensional low-energy logical subspace and projected control operators for numerical investigation.
3. **Hardware program.** Fabrication, calibration, noise characterization, gate fidelity, leakage suppression, readout, coupling, and scalability remain experimental engineering tasks.

The long-term objective is a deterministic quantum-processing architecture in which the physical graph, non-Abelian transport, and logical subspace are designed together rather than treating topology as an after-the-fact software abstraction.

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

These definitions are an architecture under investigation; they are not, by themselves, evidence of a manufactured or fault-tolerant qubit.

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
| Effective-control scale | `g_eff ≈ 0.015085` in the referenced model; model-dependent |
| Leakage gap | Must be recomputed for graph refinement, normalization and physical parameter set |
| Experimental status | Not experimentally validated |

### Evidence boundary

The value `g_eff ≈ 0.015085` is treated as a **model-dependent research parameter**, not a universal constant. A production specification must regenerate it from the exact Hamiltonian, normalization, refinement level, control convention, and selected logical subspace.

Likewise, a leakage gap must be reported as an explicit computed spectral separation for a named device model. It must not be inferred from `I∞ = −8/9`.

---

## Validation

Before calling a physical implementation a protected qubit, the following must be demonstrated numerically and experimentally:

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

The included simulator is a **minimal research core**. It is not a full Sierpiński-gasket device solver.

---

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
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture and data flow |
| [VALIDATION_PLAN.md](docs/VALIDATION_PLAN.md) | Research-to-hardware validation gates |
| [DISCLOSURE_BOUNDARY.md](docs/DISCLOSURE_BOUNDARY.md) | What is established vs proposed |
| [qpu_core.py](qpu_core.py) | Minimal numerical core |
| [tests/test_qpu_core.py](tests/test_qpu_core.py) | Core simulator tests |
| [requirements.txt](requirements.txt) | Runtime/test dependencies |
| [CITATION.cff](CITATION.cff) | Citation metadata |
| [LICENSE.md](LICENSE.md) | Business 1.0 proprietary license |

---

## Research Status

**Status: research architecture / pre-experimental.**

No statement in this repository should be read as a claim of demonstrated fault tolerance, universal error correction, arbitrary-noise immunity, commercial fabrication readiness, or experimentally measured qubit performance.

The purpose of this repository is to make the proposed architecture precise enough to be independently simulated, challenged, refined, and eventually tested.
