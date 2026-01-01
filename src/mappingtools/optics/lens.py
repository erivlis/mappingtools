import copy
from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

T = TypeVar("T")  # The source object type
U = TypeVar("U")  # The focus value type
V = TypeVar("V")  # The new focus value type


class Lens(Generic[T, U]):
    """
    A functional optic that focuses on a specific part of a data structure.

    Lenses allow you to get, set, and modify deeply nested data in an immutable way.
    They are composable using the `/` operator, similar to pathlib.

    Example:
        >>> data = {"user": {"profile": {"name": "Ariel"}}}
        >>> # Path-like composition with auto-inference for keys/indices
        >>> name_lens = Lens.key("user") / "profile" / "name"
        >>> name_lens.get(data)
        'Ariel'
        >>> # Lenses are callable (alias for get)
        >>> name_lens(data)
        'Ariel'
        >>> new_data = name_lens.set(data, "Lion")
        >>> new_data["user"]["profile"]["name"]
        'Lion'
        >>> data["user"]["profile"]["name"]  # Original is unchanged
        'Ariel'
    """

    def __init__(self, getter: Callable[[T], U], setter: Callable[[T, U], T]):
        self._getter = getter
        self._setter = setter

    def get(self, source: T) -> U:
        """Extracts the focus value from the source."""
        return self._getter(source)

    def __call__(self, source: T) -> U:
        """Alias for get(). Allows the lens to be used as a function."""
        return self.get(source)

    def set(self, source: T, value: U) -> T:
        """Sets the focus value, returning a new source object (if supported)."""
        return self._setter(source, value)

    def modify(self, source: T, func: Callable[[U], U]) -> T:
        """Modifies the focus value using a function."""
        return self.set(source, func(self.get(source)))

    def __truediv__(self, other: "Lens[U, V] | Any") -> "Lens[T, V]":
        """
        Composes this lens with another lens using the / operator.
        If 'other' is not a Lens, it is treated as a key/index item.
        """
        if isinstance(other, Lens):
            return Lens(
                getter=lambda s: other.get(self.get(s)),
                setter=lambda s, v: self.set(s, other.set(self.get(s), v)),
            )
        # Magic: Treat non-Lens as an item key/index
        return self / Lens.item(other)

    def __rtruediv__(self, other: Any) -> "Lens[Any, U]":
        """
        Allows composition when the left operand is not a Lens.
        Example: "users" / Lens.key("name")
        """
        return Lens.item(other) / self

    @staticmethod
    def key(k: Any) -> "Lens[dict, Any]":
        """Creates a lens that focuses on a dictionary key."""
        return Lens(
            getter=lambda s: s[k],
            setter=lambda s, v: {**s, k: v},  # Shallow copy for immutability
        )

    @staticmethod
    def attr(name: str) -> "Lens[Any, Any]":
        """Creates a lens that focuses on an object attribute."""
        def setter(s, v):
            # Use shallow copy to preserve immutability for objects
            try:
                new_s = copy.copy(s)
            except TypeError:
                # Fallback if object is not copyable
                new_s = s

            setattr(new_s, name, v)
            return new_s

        return Lens(
            getter=lambda s: getattr(s, name),
            setter=setter,
        )

    @staticmethod
    def index(i: int) -> "Lens[list, Any]":
        """Creates a lens that focuses on a list index."""
        def setter(s, v):
            new_list = list(s)
            new_list[i] = v
            return new_list

        return Lens(
            getter=lambda s: s[i],
            setter=setter,
        )

    @staticmethod
    def item(k: Any) -> "Lens[Any, Any]":
        """
        Creates a smart lens that focuses on an item (key or index).
        It detects the container type at runtime to ensure correct immutable setting.
        """
        def setter(s, v):
            if isinstance(s, list):
                new_s = list(s)
                new_s[k] = v
                return new_s
            elif isinstance(s, dict):
                return {**s, k: v}

            # Generic fallback for other mutable containers
            try:
                new_s = copy.copy(s)
            except Exception:
                 # If we can't copy, we might have to fail or mutate.
                 # For a library like this, failing on uncopyable types is safer than silent mutation.
                 raise TypeError(f"Cannot set item immutably on {type(s)}")
            else:
                new_s[k] = v
                return new_s

        return Lens(
            getter=lambda s: s[k],
            setter=setter,
        )

    @staticmethod
    def path(*segments: Any) -> "Lens[Any, Any]":
        """
        Creates a lens from a sequence of keys/indices.
        Example: Lens.path("users", 0, "name")
        """
        if not segments:
            raise ValueError("Path must have at least one segment")

        lens = Lens.item(segments[0])
        for segment in segments[1:]:
            lens = lens / Lens.item(segment)
        return lens
