---
icon: lucide/info
---

# Introduction

![logo.png](images/logo.png){ width="256" align=right loading=lazy }

## What is MappingTools?

This library provides utility functions for creating, manipulating, and transforming data structures, which have or
include Mapping-like characteristics.

Includes inverting dictionaries, converting class-like objects to dictionaries, creating nested defaultdicts, and
unwrapping complex objects.

## Why use MappingTools?

Built for developers who need more than just standard dictionaries.

| Problem                        | Solution                                                                                                        |
|:-------------------------------|:----------------------------------------------------------------------------------------------------------------|
| **Boilerplate Reduction**      | Use `Dictifier` to broadcast method calls to a collection of objects (`users.greet()` instead of a `for` loop). |
| **Deep JSON Diffing**          | Use `flatten()` to collapse nested JSON into single-layer paths for easy comparison.                            |
| **Data Collisions**            | Use `inverse()` to swap keys/values without losing data (automatically creates sets for duplicates).            |
| **Slow Config Loading**        | Use `MeteredDict` to profile exactly how many times your app reads specific config keys.                        |
| **Quick Serialization**        | Use `simplify()` to instantly convert Dataclasses, DateTime, and custom objects into pure Dicts.                |
| **Complex Grouping**           | Use `reshape()` to pivot lists of dicts into N-dimensional nested dictionaries (tensors).                       |
| **Key Remapping**              | Use `rename()` or `rekey()` to transform dictionary keys using functions or maps.                               |
| **Multi-Dimensional Counting** | Use `CategoryCollector` to aggregate data into multiple buckets simultaneously (e.g., by type AND by status).   |
| **Safe Deep Modification**     | Use `Lens` to immutably update nested values without cloning the entire structure manually.                     |
