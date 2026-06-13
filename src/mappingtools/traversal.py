import dataclasses
import threading
from collections.abc import Callable, Iterable, Mapping
from enum import Enum
from typing import Any, TypeVar

T = TypeVar('T')


def _require_class_type(value: Any, *, caller: str) -> type:
    if not isinstance(value, type):
        name = getattr(value, '__name__', repr(value))
        kind = type(value).__name__
        raise TypeError(
            f"{caller} accepts classes/types only; got {kind} '{name}'. "
            "Register the object's type instead."
        )
    return value


def _is_traversal_iterable(obj: Any) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, str | bytes | bytearray)


def _is_traversal_mapping(obj: Any) -> bool:
    return isinstance(obj, Mapping)


def _is_traversal_class_instance(obj: Any) -> bool:
    if isinstance(obj, type):
        return hasattr(obj, '__dict__')
    return (
        dataclasses.is_dataclass(obj)
        or hasattr(obj, '__dict__')
        or hasattr(type(obj), '__slots__')
    )


class TraversalMode(Enum):
    """Classification modes used to route traversal dispatch."""

    MAPPING = 'mapping'
    """
    Treat the object as a mapping container (dict-like key/value structure).
    Dispatch to mapping handlers and recurse into mapping values.
    """

    ITERABLE = 'iterable'
    """
    Treat the object as a structural iterable container (list/tuple/custom iterable).
    Dispatch to iterable handlers and recurse into iterable items.
    """

    CLASS = 'class'
    """
    Treat the object as a class-instance container (attribute/member expansion).
    Dispatch to class handlers when object-style traversal is intended.
    """

    LEAF = 'leaf'
    """
    Treat the object as a terminal scalar/atomic node.
    Do not recurse structurally for this value.
    """

    @classmethod
    def of(
            cls,
            obj: Any,
            registry: 'TraversalModeRegistry | None' = None,
            *,
            include_class_detection: bool = True
    ) -> 'TraversalMode':
        """Classify an object traversal mode using overrides and protocol detection."""

        if registry is not None:
            mode = registry.resolve(obj)
            if mode is not None:
                return mode

        if _is_traversal_mapping(obj):
            return cls.MAPPING

        if _is_traversal_iterable(obj):
            return cls.ITERABLE

        if include_class_detection and _is_traversal_class_instance(obj):
            return cls.CLASS

        return cls.LEAF


class TraversalModeRegistry:
    """Registry for overriding traversal mode classification by type."""

    def __init__(self) -> None:
        self._modes: dict[type, TraversalMode] = {}
        self._cache: dict[type, TraversalMode | None] = {}
        self._lock = threading.RLock()

    def register(
            self,
            obj_type: type | None = None,
            mode: TraversalMode | None = None
    ):
        """Register a type traversal mode.

        Args:
            obj_type: type | None - The type to register.
            mode: TraversalMode | None - The traversal mode to associate with the type. Defaults to None
        """

        if mode is None:
            raise ValueError("'mode' is required for type registration.")

        if obj_type is None:
            raise ValueError("'obj_type' is required for type registration.")

        obj_type = _require_class_type(obj_type, caller='register()')
        with self._lock:
            self._modes[obj_type] = mode
            self._cache.clear()

        return obj_type

    def _resolve(self, obj_type: type) -> TraversalMode | None:
        """Resolve using MRO lookup traversal."""
        for candidate in obj_type.__mro__:
            mode = self._modes.get(candidate)
            if mode is not None:
                return mode
        return None

    def resolve(self, obj_or_type: Any) -> TraversalMode | None:
        """Resolve a traversal override using MRO lookup."""
        obj_type = obj_or_type if isinstance(obj_or_type, type) else type(obj_or_type)

        # Fast path: check membership atomically
        if obj_type in self._cache:
            return self._cache[obj_type]

        # Slow path: acquire lock and resolve
        with self._lock:
            if obj_type in self._cache:
                return self._cache[obj_type]

            resolved = self._resolve(obj_type)
            self._cache[obj_type] = resolved
            return resolved

    def clear(self) -> None:
        """Clear all registered traversal overrides."""
        with self._lock:
            self._modes.clear()
            self._cache.clear()


def traversal_mode(mode: TraversalMode, *, registry: TraversalModeRegistry) -> Callable[[type[T]], type[T]]:
    """Decorator to register a traversal mode for a class in a registry.

    Args:
        mode: Traversal mode override to apply to the decorated class.
        registry: Target registry to register into.
    """
    if mode is None:
        raise ValueError("'mode' is required for traversal_mode registration.")

    def decorator(obj_type: type[T]) -> type[T]:
        registry.register(obj_type, mode)
        return obj_type

    return decorator
