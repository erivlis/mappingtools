from collections.abc import Mapping, Sequence
from typing import TypeVar

K = TypeVar("K")
N = TypeVar("N", int, float)

__all__ = [
    "dense_to_sparse_matrix",
    "dense_to_sparse_vector",
    "sparse_to_dense_matrix",
    "sparse_to_dense_vector",
]


def dense_to_sparse_vector(
    vector: Sequence[N],
    default: N = 0,
) -> dict[int, N]:
    """
    Convert a dense vector (sequence) to a sparse vector (mapping).

    Args:
        vector: The dense vector (e.g., list or tuple).
        default: The value to treat as "empty" (not stored).

    Returns:
        A dictionary mapping indices to non-default values.
    """
    return {i: v for i, v in enumerate(vector) if v != default}


def sparse_to_dense_vector(
    vector: Mapping[int, N],
    size: int | None = None,
    default: N = 0,
) -> list[N]:
    """
    Convert a sparse vector (mapping) to a dense vector (list).

    Args:
        vector: The sparse vector.
        size: The size of the resulting list. If None, inferred from max key.
        default: The value to fill for missing keys.

    Returns:
        A list of values.
    """
    if not vector:
        return [default] * (size or 0)

    if size is None:
        size = max(vector.keys()) + 1

    result = [default] * size
    for k, v in vector.items():
        if 0 <= k < size:
            result[k] = v
    return result


def dense_to_sparse_matrix(
    matrix: Sequence[Sequence[N]],
    default: N = 0,
) -> dict[int, dict[int, N]]:
    """
    Convert a dense matrix (sequence of sequences) to a sparse matrix (mapping of mappings).

    Args:
        matrix: The dense matrix.
        default: The value to treat as "empty".

    Returns:
        A nested dictionary mapping row indices to column indices to values.
    """
    result = {}
    for r, row in enumerate(matrix):
        sparse_row = {c: v for c, v in enumerate(row) if v != default}
        if sparse_row:
            result[r] = sparse_row
    return result


def sparse_to_dense_matrix(
    matrix: Mapping[int, Mapping[int, N]],
    shape: tuple[int, int] | None = None,
    default: N = 0,
) -> list[list[N]]:
    """
    Convert a sparse matrix (mapping of mappings) to a dense matrix (list of lists).

    Args:
        matrix: The sparse matrix.
        shape: A tuple (rows, cols). If None, inferred from max keys.
        default: The value to fill for missing entries.

    Returns:
        A list of lists representing the matrix.
    """
    if not matrix:
        if shape:
            return [[default] * shape[1] for _ in range(shape[0])]
        return []

    if shape is None:
        max_row = max(matrix.keys())
        max_col = 0
        for row in matrix.values():
            if row:
                max_col = max(max_col, max(row.keys()))
        shape = (max_row + 1, max_col + 1)

    rows, cols = shape
    result = [[default] * cols for _ in range(rows)]

    for r, row in matrix.items():
        if 0 <= r < rows:
            for c, v in row.items():
                if 0 <= c < cols:
                    result[r][c] = v

    return result
