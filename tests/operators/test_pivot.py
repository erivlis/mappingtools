from collections import Counter

from mappingtools.aggregation import Aggregation
from mappingtools.operators import pivot


def test_pivot_basic():
    # Arrange
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Feb", "temp": 12},
        {"city": "LON", "month": "Jan", "temp": 5},
    ]

    # Act
    result = pivot(data, index="city", columns="month", values="temp")

    # Assert
    expected = {
        "NYC": {"Jan": 10, "Feb": 12},
        "LON": {"Jan": 5},
    }
    assert result == expected


def test_pivot_last_wins():
    # Arrange
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Jan", "temp": 20},  # Duplicate
    ]

    # Act
    result = pivot(data, index="city", columns="month", values="temp", mode=Aggregation.LAST)

    # Assert
    assert result["NYC"]["Jan"] == 20


def test_pivot_first_wins():
    # Arrange
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Jan", "temp": 20},  # Duplicate
    ]

    # Act
    result = pivot(data, index="city", columns="month", values="temp", mode=Aggregation.FIRST)

    # Assert
    assert result["NYC"]["Jan"] == 10


def test_pivot_all():
    # Arrange
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Jan", "temp": 20},
    ]

    # Act
    result = pivot(data, index="city", columns="month", values="temp", mode=Aggregation.ALL)

    # Assert
    assert result["NYC"]["Jan"] == [10, 20]


def test_pivot_distinct():
    # Arrange
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Jan", "temp": 20},
    ]

    # Act
    result = pivot(data, index="city", columns="month", values="temp", mode=Aggregation.DISTINCT)

    # Assert
    assert result["NYC"]["Jan"] == {10, 20}


def test_pivot_count():
    # Arrange
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "month": "Jan", "temp": 20},
    ]

    # Act
    result = pivot(data, index="city", columns="month", values="temp", mode=Aggregation.COUNT)

    # Assert
    assert result["NYC"]["Jan"] == Counter({10: 2, 20: 1})


def test_pivot_missing_keys():
    # Arrange
    data = [
        {"city": "NYC", "month": "Jan", "temp": 10},
        {"city": "NYC", "temp": 20},  # Missing month
        {"month": "Jan", "temp": 5},  # Missing city
    ]

    # Act
    result = pivot(data, index="city", columns="month", values="temp")

    # Assert
    assert result == {"NYC": {"Jan": 10}}


def test_pivot_empty():
    # Act
    result = pivot([], index="city", columns="month", values="temp")

    # Assert
    assert result == {}


def test_pivot_sum():
    # Arrange
    data = [
        {"item": "A", "val": 10},
        {"item": "A", "val": 20},
        {"item": "B", "val": 5},
    ]
    # We use a dummy column 'v' since pivot requires index, columns, values
    data = [dict(d, col="fixed") for d in data]

    # Act
    result = pivot(data, index="item", columns="col", values="val", mode=Aggregation.SUM)

    # Assert
    assert result == {"A": {"fixed": 30.0}, "B": {"fixed": 5.0}}


def test_pivot_max():
    # Arrange
    data = [
        {"item": "A", "val": 10},
        {"item": "A", "val": 20},
        {"item": "B", "val": 5},
    ]
    data = [dict(d, col="fixed") for d in data]

    # Act
    result = pivot(data, index="item", columns="col", values="val", mode=Aggregation.MAX)

    # Assert
    assert result == {"A": {"fixed": 20.0}, "B": {"fixed": 5.0}}


def test_pivot_min():
    # Arrange
    data = [
        {"item": "A", "val": 10},
        {"item": "A", "val": 20},
        {"item": "B", "val": 5},
    ]
    data = [dict(d, col="fixed") for d in data]

    # Act
    result = pivot(data, index="item", columns="col", values="val", mode=Aggregation.MIN)

    # Assert
    assert result == {"A": {"fixed": 10.0}, "B": {"fixed": 5.0}}


def test_pivot_running_average():
    # Arrange
    data = [
        {"item": "A", "val": 10},
        {"item": "A", "val": 20},
    ]
    data = [dict(d, col="fixed") for d in data]

    # Act
    result = pivot(data, index="item", columns="col", values="val", mode=Aggregation.RUNNING_AVERAGE)

    # Assert
    # The current implementation uses: (avg + value) / 2
    # Step 1: (0 + 10) / 2 = 5.0
    # Step 2: (5.0 + 20) / 2 = 12.5
    assert result == {"A": {"fixed": 12.5}}
