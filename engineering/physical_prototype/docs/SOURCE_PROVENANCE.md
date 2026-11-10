# Source provenance

## QPU repository baseline

- Repository: `RFT-SIRM/RFT-QPU-Sierpinski`
- Baseline `main` SHA observed during audit: `1b20ba43eb23998ea01119b6bbd4bbcd22da7107`
- Existing core: `qpu_core.py` (minimal two-site SU(2) simulator)
- Existing tests: `tests/test_qpu_core.py`

## Canonical graph and connection convention

The new finite-SG builder follows the companion reference files observed on `RFT-SIRM/Evgeny-Theorem` `main` during this audit:

| Reference file | Observed blob SHA | Convention used |
|---|---|---|
| `src/graph/sg_graph.py` | `f0c19818bae4936a783edc0d01a7dd1b4745fa0f` | recursive three-copy SG graph, first-occurrence vertex ordering, faces |
| `src/operators/operators.py` | `1375dadf9c5dc2473cd77d1ededde88888252447` | one flux edge per face, vertex-index edge orientation, cyclic axis by face index |
| `src/su2/su2_utils.py` | `823a88f85bd21dd0c30777a55e82aa51d3df36a7` | Pauli matrices, SU(2) rotations and quaternion sampling |
| `formalization/EvgenyTheorem/Graph/Faces.lean` | `24c2c42426b9f3e3b30c716f4c07095e93cb3be3` | exact recursive face list and face-index axis convention |
| `formalization/EvgenyTheorem/Orientation.lean` | `bef3fcfd81987f5b9bb18c20ab44d18de3099e2e` | vertex first-occurrence order used by the Python implementation |

The new builder sorts the undirected edge list at the API boundary for deterministic exports; transport orientation remains the same ascending vertex-index convention.

## Scope guard

This package models the SU(2)-valued spinor graph used by RFT-QPU-Sierpinski. It does not import or claim to prove the signed-Z2 local-face operator or Schur/Rayleigh convergence statements from Phi-Genesis. Any future cross-project theorem must establish the operator correspondence explicitly.
