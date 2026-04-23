"""
Recipe 16: Time-Series Smoothing (MappingCollector + Aggregation.EMA)

When processing noisy time-series data (like IoT sensor readings, stock prices,
or server CPU metrics), raw values can fluctuate wildly.

This recipe demonstrates how to use `MappingCollector` with the `Aggregation.EMA`
(Exponential Moving Average) mode to automatically smooth a stream of incoming
data points in real-time, grouped by their source.
"""

from mappingtools.aggregations import Aggregation
from mappingtools.collectors import MappingCollector


def main():
    # 1. A simulated stream of noisy sensor ticks
    sensor_stream = [
        ("sensor_cpu", 45.0),
        ("sensor_mem", 60.0),
        ("sensor_cpu", 80.0), # Sudden spike!
        ("sensor_mem", 62.0),
        ("sensor_cpu", 47.0), # Drops back down
        ("sensor_cpu", 46.0),
    ]

    # 2. Initialize a stateful MappingCollector configured for EMA
    # By default, mappingtools EMA uses an alpha (smoothing factor) of 0.5
    # EMA formula: current_ema = (new_value + current_ema) * 0.5
    metrics_tracker = MappingCollector(aggregation=Aggregation.EMA)

    print("--- Processing Noisy Sensor Stream ---")

    # 3. Stream the data into the collector
    for sensor_id, value in sensor_stream:
        # We can add items one by one. The collector maintains the running EMA state.
        metrics_tracker.add(sensor_id, value)

        # We can inspect the internal mapping at any time
        current_smoothed_val = metrics_tracker.mapping[sensor_id]
        print(f"[{sensor_id}] Raw: {value:<5.1f} | Smoothed EMA: {current_smoothed_val:.2f}")

    print("\n--- Final Smoothed State ---")
    for sensor_id, final_ema in metrics_tracker.mapping.items():
        print(f"{sensor_id}: {final_ema:.2f}")


def test_main():
    main()


if __name__ == "__main__":
    main()
