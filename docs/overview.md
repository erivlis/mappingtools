---
icon: lucide/circle-ellipsis
---

# Overview

The **_MappingTools_** library is organized into several namespaces, each containing specific functionalities for
manipulating and transforming data structures.

Below is a brief description of the main namespaces within the library:

=== ":lucide-square-sigma: Collectors"

    This namespace contains classes and functions for collecting and categorizing data items into mappings.
    
    | Class                  | Description                                                                                                              |
    |------------------------|--------------------------------------------------------------------------------------------------------------------------|
    | **AutoMapper**         | A Mapping-like class that automatically generates and assigns unique, minified strings values for any new keys accessed. |
    | **CategoryCounter**    | Extends a dictionary to count occurrences of data items categorized by multiple categories.                              |
    | **MappingCollector**   | Collects key-value pairs into an internal mapping based on different modes (ALL, COUNT, DISTINCT, FIRST, LAST).          |
    | **MeteredDict**        | A dictionary that tracks changes made to it.                                                                             |
    | **nested_defaultdict** | Creates a nested `defaultdict` with specified depth and factory.                                                         |

=== ":lucide-square-asterisk: Operators"

    This namespace provides functions that perform operations on mappings.

    | Function                             | Description                                                                                            |
    |--------------------------------------|--------------------------------------------------------------------------------------------------------|
    | **distinct**                         | Yields distinct values for a specified key across multiple mappings.                                   |
    | **flatten**                          | Converts a nested mapping structure into a single-level dictionary by flattening the keys into tuples. |
    | **inverse**                          | Generates an inverse Mapping by swapping keys and values.                                              |
    | **keep** `Deprecated`                | Yields subsets of mappings by retaining the specified keys.                                            |
    | **remove** `Deprecated`              | Yields subsets mappings with the specified keys removed.                                               |
    | **stream** `Deprecated`              | Generates items from a mapping, optionally applying a factory function to each key-value pair.         |
    | **stream_dict_records** `Deprecated` | Generates dictionary records from a mapping with customizable key and value names.                     |

=== ":lucide-square-function: Transformers"

    This namespace includes functions that reshape objects while maintaining the consistency of their structure.

    | Function      | Description                                                                                        |
    |---------------|----------------------------------------------------------------------------------------------------|
    | **listify**   | Transforms complex objects into a list of dictionaries with key and value pairs.                   |
    | **minify**    | The minify function is used to shorten the keys of an object using a specified alphabet.           |
    | **simplify**  | Converts objects to strictly structured dictionaries.                                              |
    | **strictify** | Applies a strict structural conversion to an object using optional converters for keys and values. |
    | **stringify** | Converts an object into a string representation by recursively processing it based on its type.    |
