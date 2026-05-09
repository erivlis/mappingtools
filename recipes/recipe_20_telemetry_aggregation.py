"""
Recipe 20: Telemetry Aggregation (MeteredDict + Dictifier + combine)

In a distributed or multi-threaded system, you might have multiple workers
or sub-systems, each managing their own `MeteredDict` to profile performance
and access patterns.

Eventually, you need to aggregate all these isolated telemetry summaries into a
single global summary. This recipe demonstrates how to combine `Dictifier`
(to broadcast the `counts()` call across all workers) and `reduce` with
`combine(op=NumericResolver.SUM)` to flawlessly combine the deeply nested metric trees
into one.
"""

import time
from functools import reduce

from mappingtools.collectors import MeteredDict
from mappingtools.operators import combine
from mappingtools.resolvers import NumericResolver
from mappingtools.structures import Dictifier


class Worker:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        # Each worker has its own isolated configuration tracker
        self.config = MeteredDict()

    def do_work(self):
        """Simulate a worker reading configuration keys."""
        _ = self.config.get("db_host", "localhost")
        _ = self.config.get("feature_flag_x", False)

        if self.worker_id == "worker_A":
            # Worker A does extra reads
            _ = self.config.get("db_host", "localhost")

        time.sleep(0.01)


def main():
    # 1. A fleet of workers, each with their own isolated MeteredDict
    workers = {
        "worker_A": Worker("worker_A"),
        "worker_B": Worker("worker_B"),
        "worker_C": Worker("worker_C")
    }

    # 2. Simulate parallel execution
    for w in workers.values():
        w.do_work()

    print("--- 1. Gathering Telemetry from Fleet ---")

    # 3. Broadcast the `.counts()` call to the entire fleet
    # We wrap the dict of workers in a Dictifier so we can access `.config.counts()`
    # simultaneously on all of them.
    fleet = Dictifier.auto(workers)

    # This generates a dict of {"worker_A": {counts_dict}, "worker_B": ...}
    fleet_counts = fleet.config.counts()

    print(f"Collected independent summaries from {len(fleet_counts)} workers.")

    print("\n--- 2. Aggregating Global Telemetry ---")

    # 4. Merge all the independent metric trees into a single global tree
    # Because `MeteredDict.counts()` outputs a deep, consistent schema of integer counters,
    # and `combine` with `NumericResolver.SUM` operates as a Monoid (summing counters via point-wise Dictionary Merge),
    # `reduce(lambda a, b: combine(a, b, op=NumericResolver.SUM), ...)` flawlessly folds them all together.

    # We extract just the values (the actual summary dicts) to merge them.
    def sum_operator(a, b):
        return combine(a, b, op=NumericResolver.SUM)

    global_telemetry = reduce(sum_operator, fleet_counts.values())

    # 5. Display the aggregated results for specific keys
    for key in ["db_host", "feature_flag_x"]:
        total_reads = global_telemetry[key]["get"] + global_telemetry[key]["get_default"]
        print(f"Key '{key}' was accessed {total_reads} times globally.")

    # In this simulation:
    # 'feature_flag_x' was read 1 time per worker = 3 total.
    # 'db_host' was read 2 times by A, and 1 time by B and C = 4 total.


def test_main():
    main()


if __name__ == "__main__":
    main()
