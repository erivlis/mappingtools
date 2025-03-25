import string
from collections import defaultdict
from typing import Any

from mappingtools.operators import unique_strings
from mappingtools.transformers.strictify import strictify


def minify(obj: Any, alphabet=string.ascii_uppercase) -> Any:
    """Minify the keys of an object using the provided alphabet.

    Args:
        obj (Any): The object to minify.
        alphabet (str): The alphabet to use for minification.

    Returns:
        Any: The minified object.
    """

    _us = unique_strings(alphabet)

    def _next_key():
        return next(_us)

    _minified_keys = defaultdict(_next_key)

    def _minify_key(key):
        return _minified_keys[key]

    return strictify(obj, key_converter=_minify_key)
