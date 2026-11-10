# Level-1 physical demonstrator specification

## Design intent

Build the smallest nontrivial Sierpinski-gasket SU(2) cell that includes all three noncommuting Pauli axes and produces a spectrally isolated two-dimensional candidate logical subspace.

## Graph and device topology

| Item | Count / value |
|---|---:|
| SG graph vertices | 6 |
| SG graph edges | 9 |
| Elementary faces | 3 |
| Face transport axes | X, Y, Z |
| Physical mode per graph site | 2 transmons |
| Physical transmons | 12 |
| Logical candidate dimension | 2 |
| One-excitation sector dimension | 12 |
| Nonzero inter-site hopping channels | 22 |
| Intra-site beam-splitter controls | 6 |
| Differential Z-bias controls | 6 |
| Target readout resonators | 12 |

The exact edge/face indexing and frequency assignment are in `hardware/level1/`.

## Ideal numerical spectrum

At `theta = pi/2`, with unit edge weights:

| Eigenvalue index | Value / J |
|---:|---:|
| 0 | 0.12684306742643353 |
| 1 | 0.12684306742643681 (within numerical tolerance of index 0) |
| 2 | 1.520555760513274 |
| 3 | 1.520555760513274 |
| 4 | 1.832191045730923 |
| 5 | 1.832191045730924 |

The lowest pair is the candidate logical doublet. The ideal gap from the upper member of this pair to the next eigenvalue is

`Delta_leak/J = 1.3937126930868375`.

The ideal doublet splitting is at numerical roundoff (`3.28e-15 J`); this is not a predicted manufactured-device splitting.

## Illustrative frequency and coupling point

This is a starting point for circuit layout and pulse simulation, not a measured or vendor-qualified operating point:

| Parameter | Initial design assumption |
|---|---:|
| Common transmon frequency | 5.0 GHz |
| `J/(2 pi)` | 10 MHz |
| Degree-2 site frequency | 5.02 GHz |
| Degree-4 site frequency | 5.04 GHz |
| Identity-link channel magnitude | 10 MHz |
| Active X/Y channel magnitude | 7.071 MHz |
| Active Z channel magnitude | 10 MHz |
| Local intra-site drive Rabi parameter for timing estimates | 5 MHz |

At this point, `Delta_leak/(2 pi) = 13.937 MHz`. The local `g_eff` gives a nominal projected pi-pulse time

`t_pi = 1/(2 g_eff f_drive) = 0.565 microseconds`

for `f_drive = 5 MHz`. This is a Hamiltonian-level timing estimate only; pulse shaping, detuning, calibration error and leakage can lengthen it.

The site-frequency plan uses `omega_v = omega_ref + degree(v)*J` in the rotating frame. For the illustrative `J/(2 pi)=10 MHz`, degree-2 and degree-4 sites differ by 20 MHz. The X and Y face edges therefore have nonzero endpoint detuning and can use phase-defined parametric exchange. The Z face edge joins two degree-4 sites and is resonant; its diagonal hopping coefficients are complex. A single real static coupler cannot supply those phases. It needs a multi-path/static-flux or auxiliary Floquet coupler, or a re-optimized frame/frequency plan. This must be solved before tape-out. The full frequency collision map, parametric sidebands and spectator effects must be solved jointly.

## Non-Abelian check

At `theta=pi/2`, the X and Y links do not commute:

`||U_x U_y - U_y U_x||_F = 1.4142135623730947`.

The three face holonomies therefore contain genuinely noncommuting SU(2) elements in the ideal model.

## Logical controls

The best local control site is vertex 5 at coordinate `(0,1)`. The projected local-control singular values are

`[0.17704330851507566, 0.17704330851507563, 0.17704330851507563]`.

The global control singular values are

`[0.9553173669798178, 0.9026465729392008, 0.8768566804909721]`.

Both maps have rank three in the ideal simulation. The local control is easier to define and calibrate as a single anchor, whereas global control has a larger effective strength and more routing burden.

## Mandatory physical acceptance tests

A chip should not pass this gate based only on a fit to the ideal spectrum. It must demonstrate:

- all 22 complex hopping amplitudes and phases calibrated within a predeclared tolerance;
- the three face axes and non-Abelian loop products reconstructed experimentally;
- the lowest doublet isolated and tracked over repeated cooldowns;
- the measured doublet splitting and leakage gap reported with uncertainty;
- projected X/Y/Z controls full-rank and calibrated by state/process tomography;
- leakage under logical pi/2 and pi pulses measured, not inferred;
- thermal population and effective bath coupling measured;
- robustness to flux drift, residual ZZ, frequency disorder and pump phase drift;
- reset, one-excitation preparation and readout assignment errors reported.

A successful level-1 chip validates one logical qubit cell only. It does not validate a universal processor.
