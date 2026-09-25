# Architecture

## Layer 1 — Geometry

A Sierpiński-gasket graph `SG(m)` provides recursive connectivity and a controlled refinement parameter `m`.

## Layer 2 — Internal degree of freedom

Each graph site carries a two-component internal state. The intended mathematical representation is `C²`, with Pauli generators `σx`, `σy`, `σz`.

## Layer 3 — Edge transport

Selected edges carry

`U_ab = exp(-i θ σ_α / 2)`.

Different edges/triangles may select different noncommuting axes.

## Layer 4 — Hamiltonian

The graph degree contribution and transported hopping terms form the effective Hamiltonian.

## Layer 5 — Logical subspace

After diagonalization, a candidate two-dimensional low-energy subspace is selected. The selection criterion must be explicit in each numerical experiment.

## Layer 6 — Logical control

Physical/internal operators are projected into the candidate subspace. Control quality is then evaluated by matrix independence, reachable operations, pulse duration and leakage.

## Layer 7 — Hardware mapping

A physical platform must reproduce the effective Hamiltonian to sufficient accuracy. This is an open engineering stage.
