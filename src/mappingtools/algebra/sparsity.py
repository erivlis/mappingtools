from collections.abc import Mapping, Sized

__all__ = ['density', 'is_sparse', 'sparsity']


def count_elements(obj: Sized) -> int:
    """
    Recursively count the number of non-container elements in a structure.

    Args:
        obj: The object to count.

    Returns:
        The total count of leaf elements.
    """
    if isinstance(obj, Mapping):
        return sum(count_elements(v) for v in obj.values())
    # We treat strings/bytes as atomic values, not containers of characters
    if isinstance(obj, (str, bytes)):
        return 1
    # We treat other Sized iterables (lists, tuples) as containers?
    # For sparse algebra, we usually deal with Mappings.
    # If we have a list, is it a dense vector?
    # Let's stick to Mapping recursion for now to support SparseMatrix.
    return 1


def density(obj: Sized, capacity: int | None = None) -> float:
    """
    Calculate the density of a sparse object.
    Density = Number of stored elements / Total capacity.

    If the object is a nested Mapping (like a SparseMatrix), it counts
    all leaf elements recursively.

    Args:
        obj: The sparse object (e.g., dict).
        capacity: The total possible size (e.g., vector length, matrix N*M).
                  If None, density is undefined (or 1.0 relative to itself).

    Returns:
        Float between 0.0 and 1.0.
    """
    if capacity is None or capacity == 0:
        return 1.0 if len(obj) > 0 else 0.0

    # Use recursive count for Mappings to handle matrices correctly
    count = count_elements(obj) if isinstance(obj, Mapping) else len(obj)

    return count / capacity


def sparsity(obj: Sized, capacity: int | None = None) -> float:
    """
    Calculate the sparsity of an object.
    Sparsity = 1 - Density.

    Args:
        obj: The sparse object.
        capacity: The total possible size.

    Returns:
        Float between 0.0 and 1.0.
    """
    return 1.0 - density(obj, capacity)


def is_sparse(obj: Sized, capacity: int | None = None, threshold: float = 0.5) -> bool:
    """
    Check if an object is considered "sparse" based on a threshold.

    Args:
        obj: The object.
        capacity: Total capacity.
        threshold: Sparsity threshold (default 0.5).
                   If sparsity > threshold, returns True.

    Returns:
        True if sparse, False otherwise.
    """
    return sparsity(obj, capacity) > threshold
