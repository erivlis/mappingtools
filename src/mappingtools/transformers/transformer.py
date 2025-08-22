from collections import Counter
from collections.abc import Callable, Mapping
from typing import Any

from mappingtools._tools import _is_class_instance, _is_strict_iterable

CIRCULAR_REFERENCE = '...'


class Transformer:
    """
    A class to transform objects recursively based on their type.
    """

    def __init__(self,
                 mapping_handler: Callable | None = None,
                 iterable_handler: Callable | None = None,
                 class_handler: Callable | None = None,
                 default_handler: Callable | None = None,
                 *args,
                 **kwargs):
        """
        Initialize the Transformer with optional handlers for different types of objects.

        Args:
            mapping_handler (Optional[Callable]): Handler for mapping objects.
            Iterable_handler (Optional[Callable]): Handler for iterable objects.
            Class_handler (Optional[Callable]): Handler for class instances.
            Default_handler (Optional[Callable]): Default handler for other objects.
            *args: Additional positional arguments for handlers.
            **kwargs: Additional keyword arguments for handlers.
        """

        self.mapping_handler = mapping_handler
        self.iterable_handler = iterable_handler
        self.class_handler = class_handler
        self.default_handler = default_handler
        self.args = args
        self.kwargs = kwargs

        self.objects_counter = Counter()
        self.objects = {}

    def __call__(self, obj: Any):
        """
           Transform the given object using the appropriate handler.

           Args:
               obj (Any): The object to transform.

           Returns:
               Any: The transformed object.
        """
        obj_id = id(obj)
        self.objects_counter[obj_id] += 1
        if self.objects_counter[obj_id] == 1:
            transformed_obj = self._transform(obj)
            self.objects[obj_id] = transformed_obj
            return self.objects[obj_id]
        elif self.objects_counter[obj_id] == 2:
            return self.objects.get(obj_id, CIRCULAR_REFERENCE)
        return None

    def _transform(self, obj: Any):
        if callable(self.mapping_handler) and isinstance(obj, Mapping):
            return self.mapping_handler(obj, self, *self.args, **self.kwargs)
        elif callable(self.iterable_handler) and _is_strict_iterable(obj):
            return self.iterable_handler(obj, self, *self.args, **self.kwargs)
        elif callable(self.class_handler) and _is_class_instance(obj):
            return self.class_handler(obj, self, *self.args, **self.kwargs)
        elif callable(self.default_handler):
            self.objects_counter.pop(id(obj))
            return self.default_handler(obj)
        else:
            self.objects_counter.pop(id(obj))
            return obj
