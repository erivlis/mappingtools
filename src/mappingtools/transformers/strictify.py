from collections.abc import Callable
from typing import Any

from mappingtools.transformers._handlers import (
    _class_with_key_handler,
    _iterable_to_list,
    _mapping_with_key_handler,
)
from mappingtools.transformers.transformer import Transformer
from mappingtools.traversal import TraversalModeRegistry
from mappingtools.typing import Tree


def strictify(
    obj: Tree[Any],
    key_handler: Callable[[Any], str] | None = None,
    value_handler: Callable[[Any], Any] | None = None,
    traversal_registry: TraversalModeRegistry | None = None,
) -> Tree[Any]:
    """Applies strict structural conversion to the given object using optional specific handlers for keys and values.

    Args:
        obj: The object to be converted.
        key_handler: A function to handle keys of mappings and classes (optional).
        value_handler: A function to handle non-container values (optional).
        traversal_registry: Optional type registry for traversal mode overrides.

    Returns:
        The object content after applying the conversion.
    """
    processor = Transformer(
        mapping_handler=_mapping_with_key_handler,
        iterable_handler=_iterable_to_list,
        class_handler=_class_with_key_handler,
        leaf_handler=value_handler,
        default_handler=value_handler,
        key_handler=key_handler,
        traversal_registry=traversal_registry,
    )

    return processor(obj)
