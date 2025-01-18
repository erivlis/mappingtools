import dataclasses
from collections.abc import Iterable


def _is_strict_iterable(obj: Iterable) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, str | bytes | bytearray)


def _is_class_instance(obj) -> bool:
    return (dataclasses.is_dataclass(obj) and not isinstance(obj, type)) or hasattr(obj, '__dict__')
