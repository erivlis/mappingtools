import pytest

from mappingtools.aggregation import Aggregation
from mappingtools.operators import reshape


@pytest.fixture
def sales_data():
    return [
        {"country": "US", "region": "North", "product": "Apple", "sales": 100},
        {"country": "US", "region": "North", "product": "Banana", "sales": 50},
        {"country": "US", "region": "South", "product": "Apple", "sales": 80},
        {"country": "UK", "region": "London", "product": "Apple", "sales": 120},
        # Duplicate for aggregation test
        {"country": "US", "region": "North", "product": "Apple", "sales": 10},
    ]


def test_reshape_basic_hierarchy(sales_data):
    """Test creating a 3-level deep nested dictionary."""
    result = reshape(sales_data, keys=["country", "region", "product"], value="sales")

    assert result["UK"]["London"]["Apple"] == 120
    assert result["US"]["South"]["Apple"] == 80
    # Default aggregation is LAST, so 10 overwrites 100
    assert result["US"]["North"]["Apple"] == 10


def test_reshape_aggregation_sum(sales_data):
    """Test aggregation logic at the leaf nodes."""
    result = reshape(
        sales_data,
        keys=["country", "region", "product"],
        value="sales",
        aggregation=Aggregation.SUM
    )

    # 100 + 10
    assert result["US"]["North"]["Apple"] == 110


def test_reshape_aggregation_list(sales_data):
    """Test collecting values into a list."""
    result = reshape(
        sales_data,
        keys=["country", "product"],
        value="sales",
        aggregation=Aggregation.ALL
    )

    # US -> Apple appears in North (100, 10) and South (80)
    # Order depends on input stability
    assert sorted(result["US"]["Apple"]) == [10, 80, 100]


def test_reshape_transpose(sales_data):
    """Test that changing key order changes the tree structure (Transpose)."""
    # Group by Product first
    result = reshape(sales_data, keys=["product", "country"], value="sales")

    assert "Apple" in result
    assert "Banana" in result
    assert result["Banana"]["US"] == 50


def test_reshape_missing_keys():
    """Test that missing keys are handled gracefully (grouped under None)."""
    data = [
        {"a": 1, "b": 2, "val": 10},
        {"a": 1, "val": 20},  # Missing 'b'
    ]

    result = reshape(data, keys=["a", "b"], value="val", aggregation=Aggregation.SUM)

    assert result[1][2] == 10
    assert result[1][None] == 20

def test_reshape_empty():
    assert reshape([], keys=["a"], value="v") == {}


def test_reshape_deep_access_with_callable():
    """Test using callables (simulating Lenses) for deep key access."""
    data = [
        {"id": 1, "meta": {"region": "US", "type": "A"}, "sales": 100},
        {"id": 2, "meta": {"region": "UK", "type": "B"}, "sales": 200},
    ]

    # Simulate Lenses using lambdas
    # In practice: keys=[Lens("meta.region"), Lens("meta.type")]
    result = reshape(
        data,
        keys=[lambda x: x["meta"]["region"], lambda x: x["meta"]["type"]],
        value="sales"
    )

    assert result["US"]["A"] == 100
    assert result["UK"]["B"] == 200
