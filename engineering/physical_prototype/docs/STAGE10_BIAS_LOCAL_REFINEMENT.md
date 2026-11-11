# Stage 10 — local refinement around the bias-shifted full-gate candidate

Status: preliminary local optimization. The 40-step/period 3x3 scan is complete;
120-step/period convergence is complete for the selected candidate. The 240 and
480 grids remain pending. This is a closed-system numerical result, not hardware
qualification or a release-ready gate.

## Model and fixed settings

- 125-dimensional product Hilbert space (5 retained levels per mode).
- Stage-5 fixed local coupler basis, with Stage-9 DC-bias shift projected into
  that retained basis; excluded coupler levels are not re-quantized.
- Bias offset: -0.0075 Phi0; absolute bias: 0.25934367625232063 Phi0.
- Fundamental flux amplitude: 0.020 Phi0.
- Raised-cosine ramp: 8 pump periods.
- Local search at 40 steps/pump period: pump offsets -64, -63, -62 kHz from
  the shifted static A-B detuning; requested durations 1.079, 1.081, 1.083 us.
- All 9 local candidates satisfied the preliminary screen: each directional
  transfer >=0.999, final maximum logical leakage <=1e-3, sampled coupler
  population <=0.02. These thresholds are screening gates, not hardware limits.

## 40-grid local search

The highest process overlap in this 3x3 scan was obtained at:

- pump offset: -64 kHz;
- pump frequency: 987.609221499198 MHz;
- requested pulse duration: 1.081 us;
- actual 40-grid duration: 1.080994361696396 us;
- amplitude: 0.020 Phi0.

Metrics at this coarse point:

- process overlap after local-Z fit: 0.9999953294832336;
- A-to-B transfer: 0.9999912230985897;
- B-to-A transfer: 0.9999912233320231;
- iSWAP conditional phase: +0.0021068730441144764 rad;
- average logical-state fidelity including leakage (projected-matrix formula):
  0.9999962625417986;
- maximum final logical leakage: 1.8735e-8;
- maximum sampled coupler excited probability: 0.0059256414;
- maximum sampled logical leakage during the pulse: 0.0003480406;
- logical-block unitarity defect: 1.8864e-8;
- final norm error: 1.0651e-10.

## 120-grid independent candidate propagation

The same physical controls were independently propagated at 120 steps/pump
period with the common-duration convergence runner:

- actual duration: 1.081002799581697 us;
- A-to-B transfer: 0.9999840796338072;
- B-to-A transfer: 0.9999840792067629;
- process overlap after local-Z fit: 0.9999917381893985;
- conditional phase: +0.002186683862490856 rad;
- average logical-state fidelity including leakage: 0.9999933899994256;
- maximum final logical leakage: 1.0640e-8;
- maximum sampled coupler excited probability: 0.0058988304;
- maximum sampled logical leakage: 0.0003302918;
- logical-block unitarity defect: 1.06495e-8;
- final norm error: 2.1154e-10.

The 120-grid state is preserved in the accompanying resumable checkpoint.
The 240 and 480 grids have NOT been completed in this internal environment;
they must be run before treating the candidate as numerically converged.

## Comparison with Stage 9 reference at the same 120 grid

Stage 9 (bias -0.0075 Phi0, pump offset -63 kHz, requested duration 1.081 us):
process overlap 0.9999809646, A-to-B transfer 0.9999625324,
conditional phase +0.0021867027 rad.

Stage 10 (-64 kHz, same bias/amplitude/duration): process overlap
0.9999917382, A-to-B transfer 0.9999840796, conditional phase
+0.0021866839 rad.

This is a promising local improvement: both transfer and process overlap are
higher at the same 120-grid, while the conditional phase is essentially
unchanged. It is not yet evidence of a global optimum or robust operating point.

## Limitations / acceptance conditions

1. Complete the 240 and 480 grids at exactly the same physical pulse duration.
2. Compare phase-aligned full 4x4 matrices and verify second-order convergence.
3. Refine pulse amplitude, frequency, duration jointly at higher resolution.
4. Run amplitude, frequency and DC-bias perturbation sweeps; report worst-case,
   not just the nominal optimum.
5. Re-quantize the local SQUID coupler basis at the shifted DC flux and expand
   the retained charge/local-level cutoffs.
6. Add measured flux-line transfer function, bandwidth, delay, filtering,
   distortion and cross-talk.
7. Add T1/T2, thermal population, quasiparticle and fabrication/calibration
   variation models before any hardware qualification.

No experimental gate fidelity, fabrication readiness or hardware release claim
is made.
