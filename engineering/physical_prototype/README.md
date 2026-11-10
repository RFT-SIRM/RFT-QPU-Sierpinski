# RFT-QPU-Sierpinski — level-1 physical demonstrator model

**Package:** v0.1 · **Evidence status:** executable numerical prototype and proposed hardware mapping. No chip has been fabricated or measured.

This package contains the reproducible finite-graph SU(2) model, projected logical controls, a proposed 12-transmon level-1 mapping, the first two-cell projected-entangler calculation, design tables, test suite and engineering gate documents.

## Start here

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
```

Expected test result: `20 passed`.

## Reproduce the one-cell demonstrator calculation

```bash
python -m rft_qpu.cli \
  --level 1 \
  --J-MHz 10 \
  --temperature-mK 10 \
  --disorder-samples 250 \
  --output results/level1_prototype_report.json \
  --hardware-dir hardware/level1
```

## Reproduce the two-cell projected interaction

```bash
python scripts/run_two_cell.py
```

The two-cell report models 24 physical transmon modes and a proposed projected interaction. The physical coupler implementation and driven/open-system gate are not validated.

## Level-1 design summary

- 6 graph sites, 9 edges, 3 face transports (X/Y/Z).
- 2 transmon modes per graph site: 12 modes in the single-excitation model.
- ground-doublet splitting: `3.2751579226442118e-15 J` (numerical roundoff in the ideal model).
- leakage gap to the next level: `1.3937126930868375 J`.
- strongest local projected-control scale: `0.17704330851507563` at vertex 5.
- at `J/(2 pi)=10 MHz`, the model gap corresponds to `13.9371 MHz`; at 10 mK the equilibrium Boltzmann benchmark is `0.9353`. This is a warning scale, not a prediction of measured chip population.

## Project map

- `src/rft_qpu/` — graph, SU(2) links, Hamiltonian, projected controls, noise and hardware mapping.
- `tests/` — regression tests for graph construction, operator properties, control mapping, disorder and two-cell projection.
- `hardware/level1/` — frequency assumptions, BOM, coupler channels and scale tables.
- `design/level1_transmon_topology.svg` — editable topology schematic.
- `design/level1_transmon_topology.png` — raster preview.
- `results/` — numerical output reports.
- `docs/` — physical-realization notes, prototype specification, scale architecture, validation gates, risk register and source provenance.
- `VALIDATION_REPORT.md` — independent package/test/command validation and evidence boundary.

## Critical engineering blockers before fabrication

1. The complex-phase resonant Z transport needs a realizable multi-path or parametrically driven coupler and a phase/noise budget.
2. The 2-level single-excitation approximation must be replaced by a multi-level transmon + coupler circuit model, including parasitic ZZ, drive sidebands and higher-level leakage.
3. The device needs a concrete resonator/readout/reset/control layout, frequency-collision analysis, calibration plan and EM extraction.
4. Open-system simulations and measured coherence, thermal population, leakage and gate fidelity are required before any protection or processor claim.

**Do not treat the CSV channel map as a foundry netlist or the two-cell projected interaction as an experimentally realized entangling gate.**
