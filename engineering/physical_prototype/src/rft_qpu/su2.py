"""SU(2) transport matrices and gauge transformations."""
from __future__ import annotations

import numpy as np

I2 = np.eye(2, dtype=np.complex128)
SIGMA_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
SIGMA_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
SIGMA_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI = (SIGMA_X, SIGMA_Y, SIGMA_Z)
AXIS_NAMES = ("x", "y", "z")
AXIS_INDEX = {name: i for i, name in enumerate(AXIS_NAMES)}


def axis_index(axis: int | str) -> int:
    if isinstance(axis, str):
        try:
            return AXIS_INDEX[axis.lower()]
        except KeyError as exc:
            raise ValueError("axis must be x, y, z or 0, 1, 2") from exc
    if axis not in (0, 1, 2):
        raise ValueError("axis must be x, y, z or 0, 1, 2")
    return int(axis)


def su2_rotation(axis: int | str, theta: float) -> np.ndarray:
    """Return exp(-i theta sigma_axis/2)."""
    sigma = PAULI[axis_index(axis)]
    return np.cos(theta / 2.0) * I2 - 1j * np.sin(theta / 2.0) * sigma


def random_su2(rng: np.random.Generator) -> np.ndarray:
    """Haar-random SU(2) matrix generated from a unit quaternion."""
    q = rng.normal(size=4)
    norm = np.linalg.norm(q)
    if norm == 0:
        raise ArithmeticError("random quaternion unexpectedly had zero norm")
    q /= norm
    a, b, c, d = q
    return np.array(
        [[a + 1j * b, c + 1j * d], [-c + 1j * d, a - 1j * b]],
        dtype=np.complex128,
    )


def gauge_transform_transport(u_ab: np.ndarray, g_a: np.ndarray, g_b: np.ndarray) -> np.ndarray:
    return g_a @ u_ab @ g_b.conj().T


def gauge_unitary(gauges: list[np.ndarray] | tuple[np.ndarray, ...]) -> np.ndarray:
    result = np.zeros((2 * len(gauges), 2 * len(gauges)), dtype=np.complex128)
    for vertex, gauge in enumerate(gauges):
        block = slice(2 * vertex, 2 * vertex + 2)
        result[block, block] = gauge
    return result
