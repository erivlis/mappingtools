"""
Recipe 15: Pivot Tensors (reshape + Aggregation.ALL)

When dealing with analytics, you often receive rows of data that need to be
grouped by multiple intersecting axes (e.g., Year -> Quarter -> Category -> Value).

This recipe combines the powerful `reshape` function with `Aggregation.ALL` to group
a flat stream of transactional records into an N-dimensional analytical tensor without
losing any individual underlying transactions.
"""

from mappingtools.aggregation import Aggregation
from mappingtools.operators import reshape


def main():
    # 1. A simulated stream of transactional analytics records
    transactions = [
        {"year": 2024, "qtr": "Q1", "type": "Sale", "id": "t1", "amount": 100},
        {"year": 2024, "qtr": "Q1", "type": "Sale", "id": "t2", "amount": 150},
        {"year": 2024, "qtr": "Q2", "type": "Sale", "id": "t3", "amount": 200},
        {"year": 2024, "qtr": "Q1", "type": "Refund", "id": "r1", "amount": -50},
        {"year": 2025, "qtr": "Q1", "type": "Sale", "id": "t4", "amount": 300},
    ]

    # 2. Reshape into a 3D Tensor: Year -> Quarter -> Type
    # Instead of summing the amounts, we want to collect the full transaction records
    # at the leaf level for later analysis.

    # We use a Callable to return the entire `item` as the value, rather than extracting a single key.
    tensor = reshape(
        transactions,
        keys=["year", "qtr", "type"],
        value=lambda item: item,
        aggregation=Aggregation.ALL
    )

    print("--- 3D Transaction Tensor (Year -> Quarter -> Type) ---")

    # Query the tensor directly
    print("\n[Query: 2024 -> Q1 -> Sale]")
    q1_sales = tensor[2024]["Q1"]["Sale"]

    for sale in q1_sales:
        print(f"  - Transaction {sale['id']}: ${sale['amount']}")

    print(f"Total Q1 Sales: ${sum(s['amount'] for s in q1_sales)}")

    print("\n[Query: 2024 -> Q1 -> Refund]")
    q1_refunds = tensor[2024]["Q1"]["Refund"]

    for refund in q1_refunds:
        print(f"  - Transaction {refund['id']}: ${refund['amount']}")

    print(f"Total Q1 Refunds: ${sum(r['amount'] for r in q1_refunds)}")


if __name__ == "__main__":
    main()
