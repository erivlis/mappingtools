from typing import TypeAlias, TypeVar

K = TypeVar('K')
KT = TypeVar('KT')
VT = TypeVar('VT')
VT_co = TypeVar('VT_co')
Category = TypeVar('Category', bound=str | tuple | int | float)


T = TypeVar('T')

Tree: TypeAlias = T | list['Tree[T]'] | dict[str, 'Tree[T]']
"""Tree is a recursive type representing a tree structure where each node can be of type T,
a list of subtrees, or a dictionary mapping strings to subtrees."""

JsonScalar: TypeAlias = None | bool | int | float | str
"""JsonScalar represents the basic scalar types found in JSON data."""

JsonTree: TypeAlias = Tree[JsonScalar]
"""JsonTree is a recursive type representing a JSON-like tree structure
where each node can be a JSON scalar, a list of JSON trees, or a dictionary
mapping strings to JSON trees."""

EnhancedJsonTree: TypeAlias = T | JsonTree | list['EnhancedJsonTree[T]'] | dict[str, 'EnhancedJsonTree[T]']
"""EnhancedJsonTree is a recursive type that extends JsonTree by allowing
each node to also be of type T, in addition to JSON scalars, lists of enhanced
JSON trees, or dictionaries mapping strings to enhanced JSON trees."""

# As of Python 3.12 the above can be written as:
# type Tree[T] = T | list[Tree[T]] | dict[str, Tree[T]]
#
# type JsonScalar = None | bool | int | float | str
#
# type JsonTree = Tree[JsonScalar]
#
# type EnhancedJsonTree[T] = T | JsonTree | list[EnhancedJsonTree[T]] | dict[str, EnhancedJsonTree[T]]
