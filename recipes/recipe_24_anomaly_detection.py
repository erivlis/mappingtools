"""
Recipe 24: Real-Time Anomaly Detection (MappingCollector + Aggregation.EMA)

In cybersecurity, system monitoring, or algorithmic trading, detecting anomalies
(spikes or crashes) in real-time is critical.

Instead of keeping a massive array of historical data to calculate moving averages,
we can use `MappingCollector` with `Aggregation.EMA`. The Exponential Moving Average
maintains a continuous, memory-efficient baseline. By comparing incoming data points
to the established EMA baseline *before* updating it, we can instantly flag deviations
that exceed a specific threshold (e.g., a 30% spike).
"""

from mappingtools.aggregations import Aggregation
from mappingtools.collectors import MappingCollector


def main():
    # 1. A simulated stream of API response times (in milliseconds)
    # The baseline hovers around 100ms, but there are sudden spikes.
    response_times = [
        ("api_login", 95.0),
        ("api_login", 102.0),
        ("api_login", 98.0),
        ("api_login", 105.0),
        ("api_login", 450.0),  # ANOMALY! Sudden latency spike
        ("api_login", 110.0),  # Recovery
        ("api_login", 99.0),
    ]

    # 2. The Baseline Tracker (Memory Efficient EMA)
    # Alpha = 0.5 (default). It smoothly tracks the "normal" state of the system.
    baseline_tracker = MappingCollector(aggregation=Aggregation.EMA)

    # 3. The Anomaly Threshold (e.g., 50% deviation from baseline)
    threshold_percent = 0.50

    print("--- Real-Time Anomaly Detection Engine ---")

    for endpoint, current_ping in response_times:

        # A. Check the established baseline *before* updating it
        established_baseline = baseline_tracker.mapping.get(endpoint)

        if established_baseline is not None:
            # Calculate the deviation from the norm
            deviation = abs(current_ping - established_baseline) / established_baseline

            if deviation > threshold_percent:
                print(f"[ALERT] 🚨 Anomaly detected on '{endpoint}'!")
                print(
                    f"        Expected ~{established_baseline:.1f}ms, "
                    f"but got {current_ping:.1f}ms (+{deviation * 100:.0f}%)"
                )
            else:
                print(f"[OK] {endpoint}: {current_ping:.1f}ms (Baseline: {established_baseline:.1f}ms)")
        else:
            print(f"[INIT] {endpoint}: {current_ping:.1f}ms (Establishing baseline...)")

        # B. Update the baseline with the new data point
        baseline_tracker.add(endpoint, current_ping)


def test_main():
    main()


if __name__ == "__main__":
    main()
