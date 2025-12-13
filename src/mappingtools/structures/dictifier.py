import asyncio
import inspect
import types
from collections.abc import Callable, Mapping
from typing import Any, Generic, TypeVar, get_args, get_type_hints

T = TypeVar("T")


# region Helpers

def _get_hint(target: Any, attr_name: str) -> type | None:
    """Safely gets the type hint for a method's return or a field."""
    try:
        hints = get_type_hints(target)
        return hints.get(attr_name)
    except (TypeError, NameError):
        return None


def _wrap_results(results: dict[str, Any], hinted_type: type | None) -> "Dictifier[Any]":
    """Wraps results in a Dictifier, using strict mode if hinted, else auto mode."""
    if inspect.isclass(hinted_type):
        new_dictifier = Dictifier(results)
        new_dictifier._wrapped_type = hinted_type
        return new_dictifier
    # Fallback to auto-inference mode
    return Dictifier.auto(results)

# endregion


# region Proxy Creators

def _create_method_proxy(method_name: str, return_type: type | None) -> Callable:
    """Creates a specialized proxy method for a specific target method."""

    def proxy(self, *args, **kwargs):
        results = {
            key: getattr(value, method_name)(*args, **kwargs)
            for key, value in self.items()
        }
        return _wrap_results(results, return_type)

    return proxy


def _create_async_method_proxy(method_name: str, return_type: type | None) -> Callable:
    """Creates a specialized async proxy method."""

    async def proxy(self, *args, **kwargs):
        coros = {
            key: getattr(value, method_name)(*args, **kwargs)
            for key, value in self.items()
        }
        results_list = await asyncio.gather(*coros.values())
        results = dict(zip(coros.keys(), results_list))
        return _wrap_results(results, return_type)

    return proxy


def _create_property_proxy(prop_name: str, field_type: type | None) -> property:
    """Creates a specialized proxy property."""

    def getter(self):
        results = {key: getattr(value, prop_name) for key, value in self.items()}
        return _wrap_results(results, field_type)

    return property(getter)

# endregion


# region Main Class

class Dictifier(dict[str, T], Generic[T]):
    """
    A dict-like object that proxies attribute access to its values.

    This class requires an explicit type to be provided, either through
    generic type hinting (e.g., Dictifier[MyClass]) or by using the
    @dictify decorator. It will not infer the type from its contents.

    Method Chaining and Type Safety:
        When you call a proxied method, it attempts to determine the return
        type from the method's type hints. If successful, it returns a new
        strict `Dictifier`. If not, it falls back to an `AutoDictifier`
        to allow chaining via type inference.

    For a version that always infers types, see AutoDictifier.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._auto = False

    @classmethod
    def of(cls, target_class: type[T]) -> type["Dictifier[T]"]:
        """
        Creates a specialized Dictifier subclass for the given target class.

        This method inspects the target class and pre-compiles proxy methods
        for all its public methods and properties. This provides significantly
        better performance than the standard dynamic Dictifier.

        Args:
            target_class: The class to wrap.

        Returns:
            A new class that inherits from Dictifier and has specialized proxies.
        """
        if not inspect.isclass(target_class):
            raise TypeError(f"Dictifier.of() expects a class, got {type(target_class).__name__}")

        members = {}
        try:
            type_hints = get_type_hints(target_class)
        except (TypeError, NameError):
            type_hints = {}

        for name, member in inspect.getmembers(target_class):
            if name.startswith("_"):
                continue

            if inspect.isfunction(member) or inspect.ismethod(member):
                hint = _get_hint(member, "return")
                if inspect.iscoroutinefunction(member):
                    members[name] = _create_async_method_proxy(name, hint)
                else:
                    members[name] = _create_method_proxy(name, hint)

            elif isinstance(member, property):
                hint = _get_hint(member.fget, "return")
                members[name] = _create_property_proxy(name, hint)

        for name, field_type in type_hints.items():
            if name not in members and not name.startswith("_"):
                members[name] = _create_property_proxy(name, field_type)

        members.update(
            {
                "_wrapped_type": target_class,
                "Item": target_class,
                "__module__": target_class.__module__,
                "__doc__": target_class.__doc__,
            }
        )

        return type(target_class.__name__, (cls,), members)

    @classmethod
    def auto(cls, source: Mapping[str, T]) -> "Dictifier[T]":
        """Creates a Dictifier that automatically infers types from its contents."""
        d = cls(source)
        d._auto = True
        return d

    def _get_target_type(self) -> type | None:
        """Safely resolves the wrapped type from explicit declarations."""
        # 1. Check for a cached type on the instance
        target_type = self.__dict__.get("_wrapped_type")

        # 2. Check for a type on the class (decorator pattern)
        if target_type is None:
            target_type = getattr(self.__class__, "_wrapped_type", None)

        # 3. Check for a generic type hint (e.g., Dictifier[Greeter])
        if (
            target_type is None
            and (orig_class := self.__dict__.get("__orig_class__"))
            and (type_args := get_args(orig_class))
        ):
            target_type = type_args[0]
            self._wrapped_type = target_type  # Cache for future calls

        # 4. Auto-inference fallback
        if not target_type and self._auto and self:
            target_type = type(next(iter(self.values())))

        return target_type

    def __getattr__(self, name: str) -> Any:
        """Proxies attribute access to the contained objects."""
        target_type = self._get_target_type()

        if not target_type:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'. "
                "It is empty and no wrapped type was specified."
            )

        attr = getattr(target_type, name, None)

        if inspect.iscoroutinefunction(attr):
            hint = _get_hint(attr, "return")
            proxy = _create_async_method_proxy(name, hint)
            # Bind the proxy function to self so it acts like a method
            return types.MethodType(proxy, self)

        elif callable(attr):
            hint = _get_hint(attr, "return")
            proxy = _create_method_proxy(name, hint)
            # Bind the proxy function to self so it acts like a method
            return types.MethodType(proxy, self)
        else:
            # Handle fields/properties with deep proxying
            results = {key: getattr(value, name) for key, value in self.items()}
            hint = _get_hint(target_type, name)
            return _wrap_results(results, hint)

# endregion
