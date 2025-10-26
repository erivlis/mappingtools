import string
from typing import Any

from mappingtools.collectors import AutoMapper
from mappingtools.transformers.strictify import strictify


def minify(obj: Any, alphabet=string.ascii_uppercase) -> Any:
    """Minify the keys of an object using the provided alphabet.

    Args:
        obj (Any): The object to minify.
        alphabet (str): The alphabet to use for minification.

    Returns:
        Any: The minified object.
    """

    minifying_mapper = AutoMapper(alphabet)

    return strictify(obj, key_converter=minifying_mapper.get)
