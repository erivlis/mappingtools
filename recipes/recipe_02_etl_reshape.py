"""
Recipe 02: Reshaping Tabular Data (ETL / Pandas / CSV)

This recipe demonstrates how to convert a flat, tabular stream of data
(like rows from a CSV or a database cursor) into a deeply nested dictionary (tensor).

Instead of writing recursive `defaultdict` loops, we use `reshape` to group by keys
and `Aggregation` modes to resolve conflicts at the leaf nodes.
"""

from mappingtools.aggregations import Aggregation
from mappingtools.operators import reshape


def main():
    # 1. A simulated stream of flat records (e.g., from csv.DictReader or sqlite3 row factory)
    sales_stream = [
        {"region": "North", "country": "US", "product": "Widget A", "revenue": 100},
        {"region": "North", "country": "US", "product": "Widget B", "revenue": 150},
        {"region": "North", "country": "CA", "product": "Widget A", "revenue": 200},
        {"region": "South", "country": "BR", "product": "Widget C", "revenue": 50},
        # Duplicate record to demonstrate aggregation handling
        {"region": "South", "country": "BR", "product": "Widget C", "revenue": 25},
    ]

    # 2. Reshape into a 2-level hierarchy: Region -> Country
    #    We sum the revenue at the leaf level using Aggregation.SUM
    regional_revenue_tree = reshape(
        sales_stream,
        keys=["region", "country"],
        value="revenue",
        aggregation=Aggregation.SUM
    )

    print("--- Aggregated Revenue by Region -> Country ---")
    print("North America (US):", regional_revenue_tree["North"]["US"])  # Output: 250 (100 + 150)
    print("South America (BR):", regional_revenue_tree["South"]["BR"])  # Output: 75 (50 + 25)

    # 3. Reshape into a 3-level hierarchy: Region -> Country -> Product
    #    We collect all individual sales into a list at the leaf using Aggregation.ALL
    regional_product_sales = reshape(
        sales_stream,
        keys=["region", "country", "product"],
        value="revenue",
        aggregation=Aggregation.ALL
    )

    print("\n--- Detailed Sales Lists by Region -> Country -> Product ---")
    print("Widget C in BR:", regional_product_sales["South"]["BR"]["Widget C"])  # Output: [50, 25]


def test_main():
    main()


if __name__ == "__main__":
    main()
