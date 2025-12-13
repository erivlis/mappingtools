import contextlib
from collections.abc import Mapping
from typing import TypeVar, overload

from .dictifier import Dictifier
from .lazy_dictifier import LazyDictifier

# Create a convenient alias for the decorator
dictify = Dictifier.of

__all__ = (
    "Dictifier",
    "LazyDictifier",
    "dictify",
    "map_objects",
)

T = TypeVar("T")


@overload
def map_objects(
    source: Mapping[str, T],
    *,
    lazy: bool = False,
    type_hint: type[T],
) -> Dictifier[T]:
    ...


@overload
def map_objects(
    source: Mapping[str, T],
    *,
    lazy: bool = True,
    type_hint: type[T] | None = None,
) -> LazyDictifier[T]:
    ...


@overload
def map_objects(
    source: Mapping[str, T],
    *,
    lazy: bool = False,
    type_hint: None = None,
) -> Dictifier[T]:  # Returns an auto-inferring Dictifier
    ...


def map_objects(
    source: Mapping[str, T],
    *,
    lazy: bool = False,
    type_hint: type[T] | None = None,
) -> Mapping[str, T]:
    """
    Creates a proxy mapping for a collection of objects.

    This factory function provides a unified entry point for creating
    Dictifier or LazyDictifier instances based on the desired behavior.

    Args:
        source: The source mapping of objects (e.g., a dict).
        lazy: If True, returns a LazyDictifier that defers execution.
              If False (default), returns an eager Dictifier.
        type_hint: Optional class type of the objects in the source.
                   If provided, returns a strict Dictifier.
                   If None, returns a Dictifier in auto-inference mode.

    Returns:
        A Mapping that proxies attribute access to the contained objects.
    """
    if lazy:
        # LazyDictifier handles its own type inference or accepts a hint
        return LazyDictifier(source, target_type=type_hint)

    if type_hint:
        # Strict eager Dictifier
        d = Dictifier(source)
        # We need to manually set the wrapped type since we aren't using the generic constructor
        # This is a bit of a hack because Dictifier expects the type via __orig_class__ or decorator
        # But we can set the internal property directly.
        with contextlib.suppress(AttributeError):
            d._wrapped_type = type_hint
        return d

    # Inferred eager Dictifier
    return Dictifier.auto(source)
