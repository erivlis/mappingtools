import inspect
from collections.abc import Callable
from typing import Any

from mappingtools.transformers.transformer import Transformer
from mappingtools.typing import Tree


def _class_generator(obj):
    yield from ((k, v) for k, v in inspect.getmembers(obj) if not k.startswith('_'))


def _strictify_mapping(obj, processor, key_handler=None, **kwargs):
    return {
        (key_handler(k) if callable(key_handler) else k): processor(v)
        for k, v in obj.items()
    }


def _strictify_iterable(obj, processor, **kwargs):
    return [processor(v) for v in obj]


def _strictify_class(obj, processor, key_handler=None, **kwargs):
    return {
        (key_handler(k) if callable(key_handler) else k): processor(v)
        for k, v in _class_generator(obj)
    }


def strictify(
    obj: Tree[Any],
    key_handler: Callable[[Any], str] | None = None,
    value_handler: Callable[[Any], Any] | None = None,
) -> Tree[Any]:
    """Applies strict structural conversion to the given object using optional specific handlers for keys and values.

    Args:
        obj: The object to be converted.
        key_handler: A function to handle keys of mappings and classes (optional).
        value_handler: A function to handle non-container values (optional).

    Returns:
        The object content after applying the conversion.
    """
    processor = Transformer(
        mapping_handler=_strictify_mapping,
        iterable_handler=_strictify_iterable,
        class_handler=_strictify_class,
        default_handler=value_handler,
        key_handler=key_handler,
    )

    return processor(obj)
