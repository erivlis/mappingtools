"""
Recipe 05: Profiling Config Access (MeteredDict)

This recipe demonstrates how to use `MeteredDict` to track how
many times your application reads or writes specific keys.

This is incredibly useful for finding "hot keys" in a config file
that might be better served by being cached locally rather than
repeatedly fetched from a slow remote store.
"""

import time

from mappingtools.collectors import MeteredDict


def main():
    # 1. Initialize a generic "Config" dictionary, but wrap it in MeteredDict
    # This transparently hooks all `__getitem__` and `__setitem__` calls
    app_config = MeteredDict()

    # 2. Simulate loading remote config
    app_config["db_host"] = "db.local"
    app_config["api_key"] = "sk_live_12345"
    app_config["feature_flag_x"] = True

    # 3. Simulate an application loop (e.g., handling 5 requests)
    for _ in range(5):
        # We always check the db_host
        _ = app_config["db_host"]
        time.sleep(0.01) # Simulate some work

    # Simulate a rare API call
    _ = app_config["api_key"]

    # 4. Generate the telemetry summaries
    print("--- Config Access Profiling ---")
    summaries = app_config.summaries()

    # Find the hottest read keys
    for key, stats in summaries.items():
        get_count = stats["get"]["count"]
        if get_count > 0:
            print(f"Key: '{key}' was read {get_count} times.")

    print("\n--- Identifying Unused Keys ---")
    # Identify keys that were loaded but never used
    unused_keys = []
    for key, stats in summaries.items():
        if stats["get"]["count"] == 0 and stats["get_default"]["count"] == 0:
            unused_keys.append(key)

    print(f"Loaded but never read: {unused_keys}")


if __name__ == "__main__":
    main()
