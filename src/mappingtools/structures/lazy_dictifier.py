from collections.abc import Callable, Iterator, Mapping
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class LazyDictifier(Mapping[str, T], Generic[T]):
    """
    A dict-like object that lazily proxies attribute access to its values.

    Operations (method calls, attribute access) are not executed immediately.
    Instead, they build up a pipeline of operations. The pipeline is only
    executed for a specific key when that key is accessed.
    """

    def __init__(
        self,
        source: Mapping[str, Any],
        op_chain: list[Callable] | None = None,
        target_type: type | None = None,
    ):
        self._source = source
        self._op_chain = op_chain or []
        self._target_type = target_type

    def _get_target_type(self) -> type | None:
        """Resolves the wrapped type from the source or by inference."""
        if self._target_type:
            return self._target_type

        # If source is a Dictifier, inherit its type
        if hasattr(self._source, "_get_target_type"):
            return self._source._get_target_type()
        else:
            # Fallback to inference from the source's values
            if self._source:
                return type(next(iter(self._source.values())))

        return None

    def __getattr__(self, name: str) -> "LazyDictifier":
        """Adds a new operation to the chain."""

        def operation(value: Any) -> Any:
            return getattr(value, name)

        new_chain = [*self._op_chain, operation]
        # Propagate the type info
        return LazyDictifier(self._source, new_chain, self._get_target_type())

    def __call__(self, *args, **kwargs) -> "LazyDictifier":
        """Adds a method call operation to the chain."""

        def operation(value: Any) -> Any:
            return value(*args, **kwargs)

        new_chain = [*self._op_chain, operation]
        # After a call, we don't know the return type, so we don't propagate it.
        # The next getattr will have to infer from the result.
        # This is a simplification for now.
        return LazyDictifier(self._source, new_chain, None)

    def __getitem__(self, key: str) -> T:
        """Executes the operation chain for a specific key."""
        if key not in self._source:
            raise KeyError(key)

        value = self._source[key]
        for op in self._op_chain:
            value = op(value)
        return value

    def __iter__(self) -> Iterator[str]:
        """Iterates over the keys of the original source."""
        return iter(self._source)

    def __len__(self) -> int:
        """Returns the length of the original source."""
        return len(self._source)

    def __repr__(self) -> str:
        return f"LazyDictifier(source={self._source}, ops={len(self._op_chain)})"
