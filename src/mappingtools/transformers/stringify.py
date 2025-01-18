from collections.abc import Iterable
from typing import Any

from mappingtools.transformers.strictify import _class_generator
from mappingtools.transformers.transformer import Transformer


def _stringify_kv_stream(iterable: Iterable[tuple[Any, Any]],
                         processor,
                         kv_delimiter,
                         item_delimiter,
                         key_converter,
                         *args,
                         **kwargs):
    items = (f"{key_converter(k)}{kv_delimiter}{processor(v)}" for k, v in iterable)
    return item_delimiter.join(items)


def _stringify_mapping(obj, *args, **kwargs):
    return _stringify_kv_stream(obj.items(), *args, **kwargs)


def _stringify_iterable(obj, processor, kv_delimiter, item_delimiter, *args, **kwargs):
    return f'[{item_delimiter.join(processor(v) for v in obj)}]'


def _stringify_class(obj, processor, kv_delimiter, item_delimiter, *args, **kwargs):
    return _stringify_kv_stream(_class_generator(obj), processor, kv_delimiter, item_delimiter, *args, **kwargs)


def stringify(obj: Any, kv_delimiter: str = '=', item_delimiter: str = ', ') -> str:
    """Stringify recursively the given object.

    Args:
        obj (Any): The object to be stringified.
        kv_delimiter (str): The key-value delimiter. Defaults to '='.
        item_delimiter (str): The item delimiter. Defaults to ', '.

    Returns:
        str: The stringified object.
    """

    processor = Transformer(mapping_handler=_stringify_mapping,
                            iterable_handler=_stringify_iterable,
                            class_handler=_stringify_class,
                            default_handler=str,
                            kv_delimiter=kv_delimiter,
                            item_delimiter=item_delimiter,
                            key_converter=str)

    return processor(obj)
