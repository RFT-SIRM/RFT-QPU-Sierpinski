# Engineering risk register — reviewed 11 November 2026

| Risk | Current evidence | Impact | Mitigation / decision |
|---|---|---|---|
| Resonant complex Z link | The active Z face edge joins two degree-4 sites and requires complex diagonal hopping phases | A single real static resonant coupler cannot realize the required phase | Design and simulate a multi-path/static-flux or auxiliary Floquet coupler, or revise frame/frequency plan; validate before tape-out |
| Graph-wide pump collisions | First-order screen: 73 primary warnings within 10 MHz; 653 conditional harmonic/intermodulation warnings; 0 MHz minimum margin | Current nine-tone assignment is not cleared for simultaneous operation | Redesign frame offsets; measure/extract complex 22×22 pump-channel transfer; run full multitone circuit/Floquet and open-system analysis |
| Thermal scale | At J/(2π)=10 MHz, level-1 gap is 13.94 MHz; at 10 mK, kBT/h=208.37 MHz and Boltzmann benchmark is 0.935 | No passive thermal protection can be claimed at this illustrative scale | Treat initial chip as dynamically prepared demonstrator; measure bath and thermal repopulation; evaluate larger J, active cooling or alternate platforms |
| Retuned Stage 11B archive | README reports local retune and SHA-256 hashes; raw JSON/NPZ outputs are absent from the repository | Best local point is not fully reproducible from tracked artifacts | Add original outputs, manifests, environment, exact command and deterministic runner |
| Retuned retained-level convergence | Five-level 480-grid and six-level 480-grid result recorded; seven-level only 120-grid | Numerical truncation error at the selected point remains incompletely bounded | Complete seven-level 240/480 propagation and matched matrix comparisons; extend driven cutoff study |
| Pulse robustness | Local deterministic search selected one nominal point; no complete worst-case uncertainty envelope | Small nominal error may not survive parameter drift or calibration uncertainty | Sweep bias, frequency, amplitude, duration, transfer-function and correlated perturbations; report worst-case and confidence bounds |
| Closed-system approximation | Stage 11B omits T1/T2, thermal bath, flux-line transfer, pump phase noise, delay, distortion and crosstalk | Projected overlap can materially overstate physical performance | Add open-system and control-transfer models, then replace model assumptions with measurements |
| Assumed circuit parameters | Stage-3 capacitances, EC/EJ and SQUID asymmetry are declared assumptions, not layout-extracted values | Static spectrum and pulse response may shift after layout and fabrication | Layout extraction, EM simulation, independent circuit-QED review and parameter uncertainty propagation |
| Effective antiunitary symmetry breaking | Ideal SU(2) model has a Kramers-like pair; random local z fields split it | Frequency mismatch and pump-phase errors can split/rotate the candidate subspace | Calibrate mode offsets and phases; add symmetry-breaking measurements; do not claim arbitrary-noise immunity |
| Coupling disorder | 250 ideal numerical samples with positive scalar edge weights ±10% and weighted-degree diagonal preserve the pair; minimum sampled gap 1.31095 J | This restricted perturbation does not model general fabrication error | Extend to independent frequency, phase, amplitude, parasitic and lossy-coupler error distributions |
| Projected controls | Level-1 local g_eff=0.177043; level-5 g_eff=0.015085 | Refinement changes control scale and leakage gap; larger level is not automatically better | Start with level 1; compare local/global control routing and measured calibration cost |
| Two-cell interaction | Static projected coefficient 0.00783608327 χ; 6.38074 μs assumes χ/(2π)=10 MHz | No calibrated two-logical-qubit gate exists | Treat as a design target; derive four cross-Kerr channels and measure process matrix, leakage and spectator effects |
| Readout and reset | Logical state is distributed over 12 modes; no measured readout map | State preparation, assignment and tomography may dominate error | Design multiplexed resonator readout; measure reset, assignment, leakage discrimination and full logical tomography |
| Scaling overhead | Level 5 maps to 732 transmons and 1,782 intra-cell exchange channels | Higher graph level may become impractical before logical advantages are demonstrated | Keep first tile at level 1; validate modular cells before increasing graph refinement |
| IP/title and disclosure | Repo lists project-author attribution but no filing, assignment, NDA or disclosure register | Rights to file/license may be unclear; premature disclosure may harm patent options | Keep private; verify inventorship, assignments and disclosure dates; patent-counsel review before sharing |

## Disorder-study interpretation

The current level-1 Monte Carlo study changes positive scalar edge weights together with the corresponding weighted-degree diagonal. This preserves the SU(2) form and the Kramers-like degeneracy in that restricted model. It does not model independent vertex-frequency offsets, arbitrary complex phase errors, lossy couplers, pump phase noise or open-system dynamics.

The local-z-field study deliberately breaks the effective antiunitary symmetry. It is a sensitivity diagnostic, not a calibrated field-to-flux response for a fabricated transmon chip.

## Decision summary

- The numerical architecture is reproducible at the level described in the test suite.
- The Stage 11B initial full-gate baseline is archived; the later local retune is reported but not fully archived.
- The proposed level-1 circuit still has an unresolved complex Z-link implementation and an uncleared multitone plan.
- Thermal, open-system, layout, fabrication, readout and measured two-cell gate evidence remain outstanding.
- No hardware-readiness, fault-tolerance or measured-noise-resilience claim is authorised by the current evidence.
