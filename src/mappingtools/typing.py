from typing import TypeVar

K = TypeVar('K')
KT = TypeVar('KT')
VT = TypeVar('VT')
VT_co = TypeVar('VT_co')
Category = TypeVar('Category', bound=str | tuple | int | float)
