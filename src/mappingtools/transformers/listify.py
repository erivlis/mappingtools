import inspect
from collections.abc import Iterable, Mapping
from typing import Any

from mappingtools.transformers.transformer import Transformer


def _listify_mapping(obj: Mapping, processor, key_name, value_name) -> list[dict]:
    return [{key_name: k, value_name: processor(v)} for k, v in obj.items()]


def _listify_iterable(obj: Iterable, processor, key_name, value_name) -> list:
    return [processor(v) for v in obj]


def _listify_class(obj, processor, key_name, value_name):
    return [{key_name: k, value_name: processor(v)} for k, v in inspect.getmembers(obj) if not k.startswith('_')]


def listify(obj: Any, key_name: str = 'key', value_name: str = 'value') -> Any:
    """
    listify recursively the given object.

    Args:
        obj (Any): The object to unwrap.
        key_name(str): The key field name.
        value_name(str): The value field name.

    Returns:
        Any: The unwrapped object.
    """

    processor = Transformer(mapping_handler=_listify_mapping,
                            iterable_handler=_listify_iterable,
                            class_handler=_listify_class,
                            key_name=key_name,
                            value_name=value_name)

    return processor(obj)
