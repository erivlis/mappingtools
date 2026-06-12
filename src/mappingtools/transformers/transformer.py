from collections import Counter
from collections.abc import Callable
from typing import Any

from mappingtools.traversal import (
    TraversalMode,
    TraversalModeRegistry,
)
from mappingtools.typing import Tree

CIRCULAR_REFERENCE = '...'


class Transformer:
    """
    A class to transform objects recursively based on their type.
    """

    def __init__(self,
                 mapping_handler: Callable | None = None,
                 iterable_handler: Callable | None = None,
                 class_handler: Callable | None = None,
                 leaf_handler: Callable | None = None,
                 default_handler: Callable | None = None,
                 traversal_registry: TraversalModeRegistry | None = None,
                 *args,
                 **kwargs):
        """
        Initialize the Transformer with optional handlers for different types of objects.

        Args:
            mapping_handler (Optional[Callable]): Handler for mapping objects.
            iterable_handler (Optional[Callable]): Handler for iterable objects.
            class_handler (Optional[Callable]): Handler for class instances.
            leaf_handler (Optional[Callable]): Handler for leaf (non-container) objects.
            default_handler (Optional[Callable]): Generic fallback for any unhandled mode.
            *args: Additional positional arguments for handlers.
            **kwargs: Additional keyword arguments for handlers (e.g., `key_handler`).
        """
        self.mapping_handler = mapping_handler
        self.iterable_handler = iterable_handler
        self.class_handler = class_handler
        self.leaf_handler = leaf_handler
        self.default_handler = default_handler
        self.traversal_registry = traversal_registry
        self.args = args
        self.kwargs = kwargs

        self.objects_counter = Counter()
        self.objects = {}

    def __call__(self, obj: Tree[Any]) -> Tree[Any]:
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
        mode = TraversalMode.of(
            obj,
            registry=self.traversal_registry,
            include_class_detection=True,
        )

        match mode:
            case TraversalMode.MAPPING if callable(self.mapping_handler):
                return self.mapping_handler(obj, self, *self.args, **self.kwargs)
            case TraversalMode.ITERABLE if callable(self.iterable_handler):
                return self.iterable_handler(obj, self, *self.args, **self.kwargs)
            case TraversalMode.CLASS if callable(self.class_handler):
                return self.class_handler(obj, self, *self.args, **self.kwargs)
            case TraversalMode.LEAF if callable(self.leaf_handler):
                self.objects_counter.pop(id(obj))
                return self.leaf_handler(obj)
            case _ if callable(self.default_handler):
                self.objects_counter.pop(id(obj))
                return self.default_handler(obj)
            case _:
                self.objects_counter.pop(id(obj))
                return obj
