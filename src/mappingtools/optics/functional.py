from collections.abc import Mapping
from typing import Any, TypeVar

from mappingtools.optics.lens import Lens

T = TypeVar('T')


def _to_lens(path: str | Lens) -> Lens:
    """Converts a dot-separated string path to a Lens, or returns the Lens as-is."""
    if isinstance(path, Lens):
        return path

    # Naive dot splitting. For complex keys, user should pass a Lens directly.
    segments = path.split('.')
    # Convert integer strings to ints for list indexing
    parsed_segments = [int(s) if s.isdigit() else s for s in segments]
    return Lens.path(*parsed_segments)


def patch(data: T, changes: Mapping[str | Lens, Any]) -> T:
    """
    Applies a set of changes to a data structure immutably.

    Args:
        data: The source data structure.
        changes: A mapping of paths (dot-separated strings or Lenses) to new values.

    Returns:
        A new data structure with the changes applied.
    """
    result = data
    for path, value in changes.items():
        lens = _to_lens(path)
        result = lens.set(result, value)
    return result


def project(data: Any, schema: Mapping[str, str | Lens]) -> dict[str, Any]:
    """
    Projects a data structure into a new dictionary shape based on a schema.

    Args:
        data: The source data structure.
        schema: A mapping of output keys to source paths (dot-separated strings or Lenses).

    Returns:
        A new dictionary containing the projected values.

    Example:
        >>> data = {"user": {"name": "Alice", "version": 1}}
        >>> project(data, {"username": "user.name", "v": "user.version"})
        {'username': 'Alice', 'v': 1}
    """
    return {key: _to_lens(path).get(data) for key, path in schema.items()}
