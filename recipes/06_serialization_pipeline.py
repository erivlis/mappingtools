"""
Recipe 06: Quick Serialization (ETL / simplify / Dictifier)

This recipe demonstrates how to convert complex Python objects (like
dataclasses, datetime objects, and custom class instances) into
pure, JSON-serializable dictionaries using `strictify`.

Instead of writing custom `to_dict` methods or configuring standard
library `json.dumps(default=...)`, a simple value converter solves it.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from mappingtools.transformers import strictify


def main():
    # 1. Define a complex business object
    @dataclass
    class User:
        id: int
        name: str
        created_at: datetime
        tags: set[str]

    # 2. Instantiate with non-serializable standard types (datetime, set)
    user = User(
        id=42,
        name="Bob",
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        tags={"developer", "admin"}
    )

    # 3. Create a Value Transformer Function
    # strictify normally leaves non-standard primitives alone, which breaks json.dumps.
    # We define a custom value converter to handle datetime objects.
    # (Sets are automatically converted to lists by strictify).
    def serialize_values(value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    # 4. Strictify the object into standard python primitives
    # Dataclasses become dicts, datetimes become strings (ISO), sets become lists
    simplified_data = strictify(user, key_converter=str, value_converter=serialize_values)

    print("--- Simplified Data (JSON ready) ---")
    print(type(simplified_data)) # It's just a dict!

    # 5. Serialize to JSON directly
    print(json.dumps(simplified_data, indent=2))


if __name__ == "__main__":
    main()
