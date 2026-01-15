from typing import Any

from mappingtools.transformers.strictify import strictify
from mappingtools.typing import EnhancedJsonTree, Tree


def simplify(obj: Tree[Any]) -> Tree[Any]:
    """Simplify recursively the given object.

    Args:
        obj (Any): The object to be simplified.

    Returns:
        The simplified object.
    """
    return strictify(obj, key_converter=str)
