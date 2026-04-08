"""
Recipe 08: The Inverted Configuration Index (Explorer Mode)

What happens when we combine `flatten` with `MappingCollector` and `Aggregation.ALL`?
We discover a powerful auditing tool: The Inverted Index.

Imagine a massive, deeply nested configuration file. You want to know:
"Are we hardcoding the same IP address, secret, or timeout in multiple places?"

By flattening the tree into (path -> value) and then collecting the swapped tuples
into an inverted mapping of (value -> [paths]), we instantly reveal configuration duplication.
"""

from mappingtools.aggregation import Aggregation
from mappingtools.collectors import MappingCollector
from mappingtools.operators import flatten


def main():
    # 1. A complex, deeply nested configuration tree
    system_config = {
        "database": {
            "primary": {"host": "10.0.0.5", "port": 5432, "timeout": 30},
            "replica": {"host": "10.0.0.6", "port": 5432, "timeout": 30}
        },
        "cache": {
            "redis": {"host": "10.0.0.5", "port": 6379} # Duplicate IP!
        },
        "services": {
            "auth": {"url": "https://auth.internal", "timeout": 30}, # Duplicate timeout!
            "billing": {"url": "https://billing.internal", "timeout": 60}
        }
    }

    # 2. Flatten the 3D tree into a 1D mapping
    # We pass a delimiter so that the paths are automatically formatted
    # as dot-notation strings (e.g., 'database.primary.host' instead of a tuple).
    flat_config = flatten(system_config, delimiter=".")

    # 3. Create the Inverted Index
    # We use a MappingCollector with Aggregation.ALL (List Monoid).
    # By iterating over the flat config, we swap the roles of key and value,
    # adding the path to the list of paths associated with that value.
    index_collector = MappingCollector(aggregation=Aggregation.ALL)

    for path, value in flat_config.items():
        # The configuration value becomes the Key, the path becomes the aggregated Value
        index_collector.add(value, path)

    inverted_index = index_collector.mapping

    # 4. Audit the configuration for duplicated values
    print("--- Configuration Audit: Duplicated Values ---")

    for value, paths in inverted_index.items():
        # If a value is mapped to more than 1 path, it's duplicated!
        if len(paths) > 1:
            print(f"\nValue: {value!r} is hardcoded in {len(paths)} locations:")
            for path in paths:
                print(f"  - {path}")


if __name__ == "__main__":
    main()
