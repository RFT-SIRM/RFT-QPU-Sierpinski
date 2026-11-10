# Integration into RFT-QPU-Sierpinski

This is an additive engineering package intended for the private `RFT-SIRM/RFT-QPU-Sierpinski` repository.

Recommended target path:

`engineering/physical_prototype/`

It does not replace:

- the existing root `qpu_core.py`;
- existing public mathematical statements in `README.md`;
- the companion theorem implementation in `Evgeny-Theorem`;
- the separate signed-Z2 / Schur work in `Phi-Genesis`.

The new module introduces a canonical finite-SG builder and a full `2|V| x 2|V|` SU(2)-spinor Hamiltonian, with regression tests for gauge covariance, effective time-reversal symmetry, Kramers pairing, projected controls and hardware export. The source graph/face convention is pinned in `SOURCE_PROVENANCE.md`.

Suggested integration commands from the repository root after copying this directory to the target path:

```bash
python3 -m pip install -e 'engineering/physical_prototype[test]'
python3 -m pytest -q engineering/physical_prototype/tests
python3 -m rft_qpu.cli \
  --level 1 --J-MHz 10 --temperature-mK 10 \
  --output engineering/physical_prototype/results/level1_prototype_report.json \
  --hardware-dir engineering/physical_prototype/hardware/level1
```

Before any remote commit, review the additive diff, ensure the package does not conflict with root module names, run the repository's complete existing test workflow, and obtain a circuit-QED review of the transmon mapping.
