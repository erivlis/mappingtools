from collections.abc import Mapping
from typing import Any

from mappingtools.transformers._handlers import _class_generator, _iterable_to_list
from mappingtools.transformers.transformer import Transformer
from mappingtools.traversal import TraversalModeRegistry
from mappingtools.typing import EnhancedJsonTree


def _listify_mapping(obj: Mapping, processor, key_name, value_name) -> list[dict]:
    return [{key_name: k, value_name: processor(v)} for k, v in obj.items()]


def _listify_class(obj, processor, key_name, value_name):
    return [{key_name: k, value_name: processor(v)} for k, v in _class_generator(obj)]


def listify(
    obj: EnhancedJsonTree[Any],
    key_name: str = 'key',
    value_name: str = 'value',
    traversal_registry: TraversalModeRegistry | None = None,
) -> EnhancedJsonTree[Any]:
    """
    listify recursively the given object.

    Args:
        obj(Any): The object to listify.
        key_name(str): The key field name.
        value_name(str): The value field name.
        traversal_registry: Optional type registry for traversal mode overrides.

    Returns:
        Any: The unwrapped object.
    """

    processor = Transformer(
        mapping_handler=_listify_mapping,
        iterable_handler=_iterable_to_list,
        class_handler=_listify_class,
        key_name=key_name,
        value_name=value_name,
        traversal_registry=traversal_registry,
    )

    return processor(obj)
