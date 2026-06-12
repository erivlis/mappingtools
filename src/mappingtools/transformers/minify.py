import string
from typing import Any

from mappingtools.collectors import AutoMapper
from mappingtools.transformers.strictify import strictify
from mappingtools.traversal import TraversalModeRegistry
from mappingtools.typing import Tree


def minify(
    obj: Tree[Any],
    alphabet=string.ascii_uppercase,
    traversal_registry: TraversalModeRegistry | None = None,
) -> Tree[Any]:
    """Minify the keys of an object using the provided alphabet.

    Args:
        obj (Any): The object to minify.
        alphabet (str): The alphabet to use for minification.
        traversal_registry: Optional type registry for traversal mode overrides.

    Returns:
        Any: The minified object.
    """

    minifying_mapper = AutoMapper(alphabet)

    return strictify(obj, key_handler=minifying_mapper.get, traversal_registry=traversal_registry)
