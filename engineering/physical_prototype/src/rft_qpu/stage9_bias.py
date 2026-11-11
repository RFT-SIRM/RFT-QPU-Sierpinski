"""Stage-9 static flux-bias offset model in the Stage-5 fixed local basis."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import eigh

from .stage5_gate import FixedBasisModel


@dataclass(frozen=True)
class BiasShiftedCircuit:
    model: FixedBasisModel
    bias_offset_Phi0: float
    bias_flux_Phi0: float
    dressed_A_frequency_MHz: float
    dressed_B_frequency_MHz: float
    dressed_AB_detuning_MHz: float
    static_ZZ_MHz: float
    minimum_bare_overlap: float
    bare_overlaps: tuple[float, float, float, float]


def build_bias_shifted_model(base: FixedBasisModel, bias_offset_Phi0: float) -> BiasShiftedCircuit:
    """Build a new static point by adding the coupler flux offset in the retained basis.

    The local coupler basis itself remains the Stage-5 fixed-DC basis. The
    static offset is added exactly within that 5-level retained subspace,
    then the full 125x125 Hamiltonian is rediagonalized and logical states are
    independently re-tracked by bare product overlap. The time-dependent
    drive term is re-zeroed about the shifted bias to avoid double-counting.
    """
    offset = float(bias_offset_Phi0)
    if not np.isfinite(offset):
        raise ValueError("bias offset must be finite")
    levels = base.dimension_per_mode
    identity = np.eye(levels, dtype=np.complex128)
    bias = base.flux_dc_Phi0 + offset
    if not 0.0 < bias < 0.5:
        raise ValueError("shifted SQUID DC bias must remain in (0, 0.5) Phi_0")
    static_bias_term = base.delta_h_coupler(bias)
    h_bias = base.h_static_MHz + np.kron(np.kron(identity, static_bias_term), identity)
    if not np.allclose(h_bias, h_bias.conj().T, atol=2e-10):
        raise ArithmeticError("bias-shifted static Hamiltonian is not Hermitian")
    energies, vectors = eigh(h_bias, check_finite=False, driver="evd")

    states = ((0, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 1))
    indices: list[int] = []
    overlaps: list[float] = []
    for state in states:
        bare_index = state[0] * levels * levels + state[1] * levels + state[2]
        weights = np.abs(vectors[bare_index, :]) ** 2
        index = int(np.argmax(weights))
        indices.append(index)
        overlaps.append(float(weights[index]))
    if len(set(indices)) != 4:
        raise RuntimeError("bias-shifted logical states are not uniquely tracked")

    drive_bias = np.array(static_bias_term, copy=True)
    def shifted_delta_h(flux: float) -> np.ndarray:
        return base.delta_h_coupler(float(flux)) - drive_bias

    shifted_model = FixedBasisModel(
        h_static_MHz=h_bias,
        eigenvalues_MHz=energies,
        eigenvectors=vectors,
        logical_basis=vectors[:, indices],
        logical_eigen_indices=indices,
        flux_dc_Phi0=bias,
        delta_h_coupler=shifted_delta_h,
        coupler_number_matrix=base.coupler_number_matrix,
        dimension_per_mode=levels,
    )

    e00, e10, e01, e11 = (float(energies[i]) for i in indices)
    f_a = e10 - e00
    f_b = e01 - e00
    zz = e11 - e10 - e01 + e00
    return BiasShiftedCircuit(
        model=shifted_model,
        bias_offset_Phi0=offset,
        bias_flux_Phi0=float(bias),
        dressed_A_frequency_MHz=float(f_a),
        dressed_B_frequency_MHz=float(f_b),
        dressed_AB_detuning_MHz=float(abs(f_a - f_b)),
        static_ZZ_MHz=float(zz),
        minimum_bare_overlap=float(min(overlaps)),
        bare_overlaps=tuple(overlaps),
    )
