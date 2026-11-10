# RFT-QPU-Sierpinski prototype package — validation record

Validation date: 2026-11-10 (UTC session)

## Package integrity

- 44 project files copied from the original generated package.
- ZIP archive integrity checked with `unzip -t`.
- Both standalone topology assets are present: SVG source and 1200x800 PNG preview.

## Executed checks

Command:

```bash
PYTHONPATH=src python -m pytest -q
```

Result:

```text
20 passed in 1.98s
```

Reproduction command:

```bash
python -m rft_qpu.cli \
  --level 1 \
  --J-MHz 10 \
  --temperature-mK 10 \
  --disorder-samples 250 \
  --output results/level1_prototype_report.json \
  --hardware-dir hardware/level1
```

Independently rerun summary:

- graph sites: 6
- graph edges: 9
- logical-mode / transmon count: 12
- ground-doublet splitting / J: 3.2751579226442118e-15
- gap to next level / J: 1.3937126930868375
- best local projected-control scale: 0.17704330851507563
- thermal benchmark at J/(2 pi)=10 MHz and T=10 mK: exp(-Delta/kBT)=0.935300267173145

Two-cell projected-interaction calculation was rerun:

- physical modes: 24 transmons
- projected ZZ coefficient / chi: 0.007836083272491063
- idealized maximally-entangling time at chi/(2 pi)=10 MHz: 1.5951846815974806 microseconds

## Interpretation boundary

These checks establish that the numerical software package runs and reproduces its stated finite-dimensional model outputs. They do NOT establish a fabricated chip, measured spectra, measured coupler phases, coherence, gate fidelity, open-system leakage, thermal occupation, or a functioning quantum computer. The present package is a computational prototype and proposed hardware mapping, not a foundry-ready layout or tape-out package.
