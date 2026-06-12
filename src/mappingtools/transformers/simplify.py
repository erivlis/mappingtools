from typing import Any

from mappingtools.transformers.strictify import strictify
from mappingtools.traversal import TraversalModeRegistry
from mappingtools.typing import Tree


def simplify(obj: Tree[Any], traversal_registry: TraversalModeRegistry | None = None) -> Tree[Any]:
    """Simplify recursively the given object.

    Args:
        obj (Any): The object to be simplified.
        traversal_registry: Optional type registry for traversal mode overrides.

    Returns:
        The simplified object.
    """
    return strictify(obj, key_handler=str, traversal_registry=traversal_registry)
