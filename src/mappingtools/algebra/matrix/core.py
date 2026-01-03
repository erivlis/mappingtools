from collections import defaultdict
from collections.abc import Mapping
from typing import TypeVar

K = TypeVar("K")
N = TypeVar("N", int, float)
V = TypeVar("V")

__all__ = [
    "add",
    "dot",
    "inner",
    "kronecker_delta",
    "mat_vec",
    "power",
    "trace",
    "transpose",
    "vec_mat",
]


def add(m1: Mapping[K, Mapping[K, N]], m2: Mapping[K, Mapping[K, N]]) -> dict[K, dict[K, N]]:
    """
    Perform element-wise addition of two sparse matrices (nested mappings).

    Args:
        m1: The first matrix.
        m2: The second matrix.

    Returns:
        A new nested dictionary representing the sum.
    """
    keys = set(m1.keys()) | set(m2.keys())
    result = {}
    for r in keys:
        row1 = m1.get(r, {})
        row2 = m2.get(r, {})
        col_keys = set(row1.keys()) | set(row2.keys())
        new_row = {}
        for c in col_keys:
            val = row1.get(c, 0) + row2.get(c, 0)
            if val != 0:
                new_row[c] = val
        if new_row:
            result[r] = new_row
    return result


def dot(m1: Mapping[K, Mapping[K, N]], m2: Mapping[K, Mapping[K, N]]) -> dict[K, dict[K, N]]:
    """
    Perform matrix multiplication (dot product) of two sparse matrices.

    Args:
        m1: The first matrix (left operand).
        m2: The second matrix (right operand).

    Returns:
        A new nested dictionary representing the product.
    """
    result = {}
    for r, row1 in m1.items():
        new_row = defaultdict(int)
        for k, val1 in row1.items():
            if k in m2:
                for c, val2 in m2[k].items():
                    new_row[c] += val1 * val2

        # Remove zeros to maintain sparsity
        cleaned_row = {c: v for c, v in new_row.items() if v != 0}
        if cleaned_row:
            result[r] = cleaned_row
    return result


def inner(v1: Mapping[K, N], v2: Mapping[K, N]) -> N:
    """
    Compute the inner product (dot product) of two vectors.

    Args:
        v1: The first vector.
        v2: The second vector.

    Returns:
        The scalar dot product.
    """
    common = set(v1.keys()) & set(v2.keys())
    return sum(v1[k] * v2[k] for k in common)


def kronecker_delta(i: K, j: K) -> int:
    """
    Compute the Kronecker delta.
    δ_ij = 1 if i == j, else 0.

    Args:
        i: First index.
        j: Second index.

    Returns:
        1 if i == j, else 0.
    """
    return 1 if i == j else 0


def mat_vec(matrix: Mapping[K, Mapping[K, N]], vector: Mapping[K, N]) -> dict[K, N]:
    """
    Multiply a matrix by a vector (M * v).

    Args:
        matrix: The matrix.
        vector: The vector.

    Returns:
        The resulting vector.
    """
    result = {}
    for r, row in matrix.items():
        # row * vector (inner product)
        val = inner(row, vector)
        if val != 0:
            result[r] = val
    return result


def power(matrix: Mapping[K, Mapping[K, N]], n: int) -> dict[K, dict[K, N]]:
    """
    Compute the n-th power of a square matrix using binary exponentiation.

    Args:
        matrix: The input matrix.
        n: The exponent (must be non-negative).

    Returns:
        The result of matrix ** n.
    """
    if n < 0:
        raise ValueError("Exponent must be non-negative.")

    # Identity matrix construction
    keys = set(matrix.keys()) | {k for row in matrix.values() for k in row}
    result = {k: {k: 1} for k in keys}

    base = matrix
    while n > 0:
        if n % 2 == 1:
            result = dot(result, base)
        base = dot(base, base)
        n //= 2
    return result


def trace(matrix: Mapping[K, Mapping[K, N]]) -> N:
    """
    Calculate the trace of a matrix (sum of diagonal elements).

    Args:
        matrix: The input matrix.

    Returns:
        The sum of diagonal elements.
    """
    return sum(row.get(r, 0) for r, row in matrix.items())


def transpose(matrix: Mapping[K, Mapping[K, V]]) -> dict[K, dict[K, V]]:
    """
    Transpose a sparse matrix (swap rows and columns).

    Args:
        matrix: The input matrix (nested mapping).

    Returns:
        A new nested dictionary with rows and columns swapped.
    """
    result = defaultdict(dict)
    for r, row in matrix.items():
        for c, val in row.items():
            result[c][r] = val

    # Convert defaultdicts to regular dicts
    return {k: dict(v) for k, v in result.items()}


def vec_mat(vector: Mapping[K, N], matrix: Mapping[K, Mapping[K, N]]) -> dict[K, N]:
    """
    Multiply a vector by a matrix (v * M).

    Args:
        vector: The vector.
        matrix: The matrix.

    Returns:
        The resulting vector.
    """
    result = defaultdict(int)
    for k, val in vector.items():
        if k in matrix:
            for c, m_val in matrix[k].items():
                result[c] += val * m_val
    return {k: v for k, v in result.items() if v != 0}
