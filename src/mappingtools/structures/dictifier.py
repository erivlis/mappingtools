import asyncio
import inspect
from collections.abc import Callable
from typing import Any, Generic, TypeVar, get_args, get_type_hints, overload

T = TypeVar("T")


def dictify(cls: type[T]) -> type["Dictifier[T]"]:
    """
    A class decorator that transforms a class into a Dictifier collection.

    The decorated class becomes a specialized subclass of Dictifier, configured
    to wrap instances of the original class.

    Usage:
        @dictify
        class UserCollection:
            # This class body defines the interface for the items.
            def __init__(self, name: str):
                self.name = name

            def greet(self):
                return f"Hi, I'm {self.name}"

        # UserCollection is now a Dictifier for UserCollection.Item
        users = UserCollection({
            "admin": UserCollection.Item("Admin"),
            "guest": UserCollection.Item("Guest"),
        })
        greetings = users.greet()  # -> {'admin': "Hi, I'm Admin", ...}
    """
    return type(
        cls.__name__,
        (Dictifier,),
        {
            "_wrapped_type": cls,
            "Item": cls,
            "__module__": cls.__module__,
            "__doc__": cls.__doc__,
        },
    )


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
            # Handle async methods
            async def async_method_proxy(*args, **kwargs) -> "Dictifier[Any]":
                coros = {
                    key: getattr(value, name)(*args, **kwargs)
                    for key, value in self.items()
                }
                results_list = await asyncio.gather(*coros.values())
                results = dict(zip(coros.keys(), results_list))

                try:
                    type_hints = get_type_hints(attr)
                    return_type = type_hints.get("return")
                except (TypeError, NameError):
                    return_type = None

                if return_type and return_type is not Any:
                    new_dictifier = Dictifier(results)
                    new_dictifier._wrapped_type = return_type
                    return new_dictifier
                else:
                    return AutoDictifier(results)

            return async_method_proxy

        elif callable(attr):
            # Handle sync methods
            def method_proxy(*args, **kwargs) -> "Dictifier[Any]":
                results = {
                    key: getattr(value, name)(*args, **kwargs)
                    for key, value in self.items()
                }

                try:
                    type_hints = get_type_hints(attr)
                    return_type = type_hints.get("return")
                except (TypeError, NameError):
                    return_type = None

                if return_type and return_type is not Any:
                    new_dictifier = Dictifier(results)
                    new_dictifier._wrapped_type = return_type
                    return new_dictifier
                else:
                    return AutoDictifier(results)

            return method_proxy
        else:
            # Handle fields/properties with deep proxying
            results = {key: getattr(value, name) for key, value in self.items()}

            # Try to find the type hint for the field
            try:
                type_hints = get_type_hints(target_type)
                field_type = type_hints.get(name)
            except (TypeError, NameError):
                field_type = None

            # Check if the field type is a class (and not a primitive)
            # to decide if we should wrap it for deep proxying.
            if inspect.isclass(field_type):
                new_dictifier = Dictifier(results)
                new_dictifier._wrapped_type = field_type
                return new_dictifier
            else:
                # If no hint or it's a primitive, fall back to AutoDictifier
                # which will wrap if the values are objects, or just return dict
                return AutoDictifier(results)


class AutoDictifier(Dictifier[T], Generic[T]):
    """
    An extension of Dictifier that automatically infers the wrapped type
    from its contents if no explicit type is provided.

    This is convenient for interactive use but can be risky with mixed-type
    collections. It determines the type from the first item in the dict.
    """

    def _get_target_type(self) -> type | None:
        """
        Resolves the wrapped type, falling back to inference from values.
        """
        # First, try the safe methods from the parent class.
        target_type = super()._get_target_type()

        # If no explicit type was found and the dict is not empty, infer it.
        if not target_type and self:
            target_type = type(next(iter(self.values())))

        return target_type
