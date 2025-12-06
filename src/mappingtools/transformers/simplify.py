from typing import Any

from mappingtools.transformers.strictify import strictify


def simplify(obj: Any) -> Any:
    """Simplify recursively the given object.

    Args:
        obj (Any): The object to be simplified.

    Returns:
        The simplified object.
    """
    return strictify(obj, key_converter=str)
