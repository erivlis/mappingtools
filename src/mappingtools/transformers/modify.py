from collections.abc import Callable
from typing import Any

from mappingtools.transformers.transformer import Transformer
from mappingtools.typing import Tree


def _modify_mapping(obj, processor, key_handler=None, **kwargs):
    return {
        (key_handler(k) if callable(key_handler) else k): processor(v)
        for k, v in obj.items()
    }


def _modify_iterable(obj, processor, **kwargs):
    return [processor(v) for v in obj]


def modify(
    obj: Tree[Any],
    key_handler: Callable[[Any], str] | None = None,
    value_handler: Callable[[Any], Any] | None = None,
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
        obj: The object to be traversed and modified.
        key_handler: A function to apply to each mapping key (optional).
        value_handler: A function to apply to each leaf value (optional).

    Returns:
        A new object with keys and/or leaves transformed.
    """
    processor = Transformer(
        mapping_handler=_modify_mapping,
        iterable_handler=_modify_iterable,
        # By not setting a class_handler, the Transformer will use the default_handler
        # for class instances, which is the correct behavior for treating them as leaves.
        default_handler=value_handler,
        key_handler=key_handler,
    )

    return processor(obj)
