# Engineering risk register

| Risk | Evidence / calculation | Impact | Required mitigation / decision |
|---|---|---|---|
| Thermal scale is too small for passive memory | At level 1 and `J/(2 pi)=10 MHz`, gap is 13.94 MHz; at 10 mK, `kBT/h` is 208.37 MHz and the equilibrium Boltzmann benchmark is 0.935 | Cannot claim passive thermal protection from this gap | Treat first chip as a dynamically prepared demonstrator; measure bath coupling and thermal repopulation; investigate stronger J, active cooling and alternative platforms |
| Parametric link count / pump crosstalk | Level 1 needs 22 effective exchange channels; frequency collisions depend on actual device spectrum | Incorrect phases/amplitudes alter SU(2) links and the spectrum | Joint frequency-plan and pump-spectrum optimization before tape-out |
| Resonant complex Z link | The level-1 Z face edge joins two degree-4 sites (zero detuning in the initial frequency plan) but requires opposite complex diagonal phases | A single real resonant coupler cannot provide the required phase | Design a multi-path/static-flux or auxiliary Floquet coupler, or re-optimize the frequency/frame convention; validate before tape-out |
| Effective antiunitary symmetry breaking | Ideal SU(2) model has Kramers-like pair; random local z fields split it | Logical splitting / dephasing | Calibrate and bound differential mode shifts and pump phase errors; add symmetry-breaking diagnostics |
| Coupling disorder | 250 numerical samples at +/-10% positive scalar edge weights preserve the doublet but reduce minimum gap to 1.311 J in the sample | Gap degradation and localization | Measure each link; use weighted Hamiltonian fitting; set per-edge tolerance from open-system simulation |
| Local controls | Level-1 best local `g_eff=0.177`; level-5 falls to 0.015085 | Large refinement weakens local logical drive and slows gates | Start level 1; compare local vs global controls; optimize controls before increasing refinement |
| Entangling gate undefined experimentally | One cell has no second logical qubit; four cross-Kerr terms are only a design target | No universal processor without entanglers | Make two-cell gate a mandatory Gate 3; do not claim a complete computer before it passes |
| Transmon higher-level leakage | Ideal calculation uses a two-component single-excitation model | Real transmons are multilevel and driven | Simulate at least 3 levels per transmon and coupler; measure leakage during parametric pulses |
| Readout of a distributed logical state | The encoded state is delocalized across 12 modes | A single readout is insufficient for tomography | Calibrate full measurement map, multiplex readout and state reconstruction |
| Scaling costs | Level 5 already maps to 732 transmons and 1,782 inter-site effective channels per cell | Direct large-level implementation may be impractical | Keep first tile at level 1; compare a distributed/digital encoding before scaling the SG level |
| Mathematical model transfer | Different RFT operator families and graph conventions must remain separate | Invalid inference from companion projects | Keep provenance, operator definition and graph convention pinned in every result |

## Disorder study interpretation

In the current level-1 Monte Carlo model, positive scalar edge-weight changes are accompanied by the corresponding weighted degree diagonal. This preserves the SU(2) form and the Kramers-like degeneracy. It does **not** model arbitrary fabrication errors, independent vertex-frequency offsets, lossy couplers, pump phase noise or open-system dynamics.

The local z-field study is intentionally time-reversal-breaking. Its mean doublet splitting grows with the field amplitude; this is a sensitivity diagnostic, not a field-to-flux calibration for a real transmon chip.
