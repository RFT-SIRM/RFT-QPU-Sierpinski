"""Canonical finite Sierpinski-gasket graph construction.

The recursion, vertex first-occurrence ordering, face ordering and flux-edge
convention follow the reference implementation in RFT-SIRM/Evgeny-Theorem.
Edges are sorted at the API boundary to make hardware export deterministic;
this does not change their vertex-index orientation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

Point: TypeAlias = tuple[float, float]
EdgePair: TypeAlias = tuple[int, int]
Face: TypeAlias = tuple[int, int, int]


@dataclass(frozen=True)
class SGGraph:
    level: int
    vertices: tuple[Point, ...]
    edges: tuple[EdgePair, ...]
    faces: tuple[Face, ...]

    @property
    def n_vertices(self) -> int:
        return len(self.vertices)

    @property
    def n_edges(self) -> int:
        return len(self.edges)

    @property
    def n_faces(self) -> int:
        return len(self.faces)

    @property
    def degrees(self) -> tuple[int, ...]:
        result = [0] * self.n_vertices
        for a, b in self.edges:
            result[a] += 1
            result[b] += 1
        return tuple(result)

    @property
    def flux_edges(self) -> tuple[EdgePair, ...]:
        """One designated (first, second) face edge per elementary face."""
        return tuple(tuple(sorted((face[0], face[1]))) for face in self.faces)


def expected_counts(level: int) -> tuple[int, int, int]:
    if level < 0:
        raise ValueError("level must be nonnegative")
    return (
        (3 ** (level + 1) + 3) // 2,
        3 ** (level + 1),
        0 if level == 0 else 3**level,
    )


def build_sg_graph(level: int) -> SGGraph:
    """Build SG(level) using the same recursive three-copy convention.

    At level zero the graph is a triangle and has no designated face list,
    matching the companion reference's convention. Level one is the first
    level with three elementary faces and three non-Abelian edge transports.
    """
    if level < 0:
        raise ValueError("level must be nonnegative")

    vertices: list[Point] = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    edges: list[EdgePair] = [(0, 1), (1, 2), (0, 2)]
    faces: list[Face] | None = None

    for _ in range(level):
        offsets = ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5))
        new_vertices: list[Point] = []
        vertex_index: dict[Point, int] = {}
        new_edges: set[EdgePair] = set()
        maps: list[dict[int, int]] = []

        for ox, oy in offsets:
            local_map: dict[int, int] = {}
            for old_index, (x, y) in enumerate(vertices):
                point = (round(x * 0.5 + ox, 10), round(y * 0.5 + oy, 10))
                if point not in vertex_index:
                    vertex_index[point] = len(new_vertices)
                    new_vertices.append(point)
                local_map[old_index] = vertex_index[point]
            maps.append(local_map)

        new_faces: list[Face] = []
        for local_map in maps:
            for a, b in edges:
                new_edges.add(tuple(sorted((local_map[a], local_map[b]))))
            if faces is None:
                new_faces.append((local_map[0], local_map[1], local_map[2]))
            else:
                new_faces.extend(
                    tuple(local_map[v] for v in face) for face in faces
                )

        vertices = new_vertices
        edges = sorted(new_edges)
        faces = new_faces

    result = SGGraph(
        level=level,
        vertices=tuple(vertices),
        edges=tuple(tuple(sorted(edge)) for edge in edges),
        faces=tuple(faces or ()),
    )
    expected = expected_counts(level)
    actual = (result.n_vertices, result.n_edges, result.n_faces)
    if actual != expected:
        raise ArithmeticError(f"SG count mismatch at level {level}: {actual} != {expected}")
    if len(set(result.flux_edges)) != result.n_faces:
        raise ArithmeticError("face-to-flux-edge assignment is not injective")
    if not set(result.flux_edges) <= set(result.edges):
        raise ArithmeticError("a designated flux edge is absent from SG graph")
    return result
