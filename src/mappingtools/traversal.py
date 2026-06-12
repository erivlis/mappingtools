from collections.abc import Iterable, Mapping
from enum import Enum
from typing import Any

from mappingtools._tools import _is_class_instance


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
        include_class_detection: bool = True,
    ) -> 'TraversalMode':
        """Classify an object traversal mode using overrides and protocol detection."""
        if registry is not None:
            mode = registry.resolve(obj)
            if mode is not None:
                return mode

        if isinstance(obj, Mapping):
            return cls.MAPPING

        is_iterable = isinstance(obj, Iterable) and not isinstance(obj, str | bytes | bytearray)
        if is_iterable:
            return cls.ITERABLE

        if include_class_detection and _is_class_instance(obj):
            return cls.CLASS

        return cls.LEAF

class TraversalModeRegistry:
    """Registry for overriding traversal mode classification by type."""

    def __init__(self) -> None:
        self._modes: dict[type, TraversalMode] = {}

    def register(self, typ: type | None = None, mode: TraversalMode | None = None):
        """Register a type traversal mode, imperatively or as a decorator."""
        if typ is None:
            if mode is None:
                raise ValueError("'mode' is required for decorator registration.")

            def decorator(cls: type) -> type:
                self._modes[cls] = mode
                return cls

            return decorator

        if mode is None:
            raise ValueError("'mode' is required for type registration.")

        self._modes[typ] = mode
        return typ

    def resolve(self, obj_or_type: Any) -> TraversalMode | None:
        """Resolve a traversal override using MRO lookup."""
        obj_type = obj_or_type if isinstance(obj_or_type, type) else type(obj_or_type)
        for candidate in obj_type.__mro__:
            mode = self._modes.get(candidate)
            if mode is not None:
                return mode
        return None

    def clear(self) -> None:
        """Clear all registered traversal overrides."""
        self._modes.clear()
