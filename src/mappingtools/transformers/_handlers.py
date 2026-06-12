import inspect
from collections.abc import Callable, Generator
from typing import Any


def _class_generator(obj: Any) -> Generator[tuple[str, Any], Any, None]:
    """Yield public class members as key/value pairs."""
    yield from ((k, v) for k, v in inspect.getmembers(obj) if not k.startswith('_'))


def _mapping_with_key_handler(
        obj: Any,
        processor: Callable[[Any], Any],
        key_handler: Callable[[Any], Any] | None = None,
        **kwargs,
) -> dict[Any, Any]:
    """Transform mapping values recursively and optionally transform keys."""
    return {
        (key_handler(k) if callable(key_handler) else k): processor(v)
        for k, v in obj.items()
    }


def _iterable_to_list(obj: Any, processor: Callable[[Any], Any], **kwargs) -> list[Any]:
    """Transform iterable items recursively into a list."""
    return [processor(v) for v in obj]


def _class_with_key_handler(
        obj: Any,
        processor: Callable[[Any], Any],
        key_handler: Callable[[Any], Any] | None = None,
        **kwargs,
) -> dict[Any, Any]:
    """Transform class members recursively and optionally transform member names."""
    return {
        (key_handler(k) if callable(key_handler) else k): processor(v)
        for k, v in _class_generator(obj)
    }
