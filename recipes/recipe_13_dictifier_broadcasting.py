"""
Recipe 13: Broadcasting Method Calls (Dictifier)

When you manage a collection of identical objects (like a pool of database
connections, a roster of users, or a fleet of sensors) indexed in a dictionary,
you often have to write boilerplate `for key, obj in collection.items(): obj.do_work()` loops.

The `Dictifier` wrapper uses metaprogramming to proxy attribute access and
method calls to all underlying objects simultaneously, collecting the results
back into a dictionary with the exact same keys.
"""

from mappingtools.structures import Dictifier


class Sensor:
    def __init__(self, name: str, temp: float):
        self.name = name
        self._temp = temp

    def read_temperature(self) -> float:
        """Simulate reading a sensor value."""
        return self._temp

    def recalibrate(self, offset: float) -> "Sensor":
        """Simulate adjusting the sensor, returning self for chaining."""
        self._temp += offset
        return self

def main():
    # 1. A dictionary of standard Python objects
    sensors = {
        "engine_bay": Sensor("Engine", 95.5),
        "cabin": Sensor("Cabin", 22.0),
        "exhaust": Sensor("Exhaust", 310.2)
    }

    # 2. Wrap the collection in a Dictifier
    # We specify `Sensor` so it knows exactly what methods are available for auto-complete/proxying
    fleet = Dictifier.of(Sensor)(sensors)

    # 3. Broadcast an attribute access (.name)
    # This automatically fetches the `.name` attribute from every sensor
    # and returns a new Dictifier containing the results.
    names = fleet.name
    print("--- Sensor Names ---")
    print(names) # Output: {'engine_bay': 'Engine', 'cabin': 'Cabin', 'exhaust': 'Exhaust'}

    # 4. Broadcast a method call (.read_temperature())
    # This calls the method on every sensor and collects the return values
    readings = fleet.read_temperature()
    print("\n--- Initial Temperature Readings ---")
    print(readings)

    # 5. Method Chaining
    # Because `recalibrate` returns a `Sensor`, the resulting Dictifier
    # is also a fleet of sensors. We can immediately chain `.read_temperature()` on it.
    print("\n--- Readings After Recalibration (-2.0 offset) ---")
    new_readings = fleet.recalibrate(offset=-2.0).read_temperature()
    print(new_readings)


def test_main():
    main()


if __name__ == "__main__":
    main()
