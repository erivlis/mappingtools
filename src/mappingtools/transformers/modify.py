from collections.abc import Callable
from typing import Any

from mappingtools.transformers._handlers import (
    _iterable_to_list,
    _mapping_with_key_handler,
)
from mappingtools.transformers.transformer import Transformer
from mappingtools.traversal import TraversalModeRegistry
from mappingtools.typing import Tree


def modify(
    obj: Tree[Any],
    key_handler: Callable[[Any], str] | None = None,
    value_handler: Callable[[Any], Any] | None = None,
    traversal_registry: TraversalModeRegistry | None = None,
) -> Tree[Any]:
    """Recursively traverses a data structure, applying handler functions to keys and leaves.

    This function navigates through mappings (like dicts) and iterables (like lists),
    but does not traverse into class instances. It treats class instances and all
    other non-container types (int, str, etc.) as "leaf" nodes.

    - `key_handler`: Applied to the keys of all mappings.
    - `value_handler`: Applied to all leaf nodes.

    The structure of the original object is preserved. The function returns a new
    object and does not mutate the input's structure in-place.

    !!! warning
        Because class instances are treated as leaf nodes, they are passed directly
        to the `value_handler`. If the `value_handler` mutates the instance's
        attributes, the original object will be changed in-place. This is in
        contrast to `strictify`, which traverses into class instances and thus
        creates a new object.

    Args:
        obj: Tree[Any] - The object to be traversed and modified.
        key_handler: Callable[[Any], str] | None - A function to apply to each mapping key (optional).
        value_handler: Callable[[Any], Any] | None - A function to apply to each leaf value (optional).
        traversal_registry: Optional type registry for traversal mode overrides.

    Returns:
        A new object, with keys and/or leaves transformed.
    """
    processor = Transformer(
        mapping_handler=_mapping_with_key_handler,
        iterable_handler=_iterable_to_list,
        # By not setting a class_handler, class instances fall through to default_handler.
        # We also set leaf_handler explicitly for terminal scalar handling.
        leaf_handler=value_handler,
        default_handler=value_handler,
        key_handler=key_handler,
        traversal_registry=traversal_registry,
    )

    return processor(obj)
