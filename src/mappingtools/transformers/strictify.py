import inspect
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from mappingtools.transformers.transformer import Transformer


def _class_generator(obj):
    yield from ((k, v) for k, v in inspect.getmembers(obj) if not k.startswith('_'))


def _strictify_mapping(obj, processor, key_converter, value_converter):
    return {
        (key_converter(k) if key_converter else k): processor(value_converter(v) if value_converter else v)
        for k, v in obj.items()}


def _strictify_iterable(obj, processor, key_converter, value_converter):
    return [processor(value_converter(v) if value_converter else v) for v in obj]


def _strictify_class(obj, processor, key_converter, value_converter):
    return {
        (key_converter(k) if key_converter else k): processor(value_converter(v) if value_converter else v)
        for k, v in _class_generator(obj)
    }


def strictify(obj: Any,
              key_converter: Callable[[Any], str] | None = None,
              value_converter: Callable[[Any], Any] | None = None) -> Any:
    """Applies strict structural conversion to the given object using optional specific converters for keys and values.

       Args:
           obj: The object to be converted.
           key_converter: A function to convert keys (optional).
           value_converter: A function to convert values (optional).

       Returns:
           The object content after applying the conversion.
       """

    if callable(value_converter):

        _value_converter = value_converter

        def value_wrapper(value: Any) -> Any:
            match value:
                case Mapping() | Iterable() | str():
                    return value
                case _:
                    return _value_converter(value)

        value_converter = value_wrapper

    processor = Transformer(mapping_handler=_strictify_mapping,
                            iterable_handler=_strictify_iterable,
                            class_handler=_strictify_class,
                            key_converter=key_converter,
                            value_converter=value_converter)

    return processor(obj)
