"""
You can skip certain columns from being serialized/deserialized.
This is useful for fields that should not be stored or transmitted.

Skipped fields should default values that are used during deserialization.
"""

from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String, Bool, Date, Skip
from typing import Annotated

import datetime


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    description: Annotated[str, Skip] = "No description"
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]


def main():
    user = User(
        user_id=123,
        username="admin",
        description="I am root",
        is_active=True,
        join_date=datetime.date.today(),
    )

    print("Original User Model:")
    print(user)

    # Serialize to bytes
    serialized = user.serialize()
    print("\nSerialized Bytes:")
    print(serialized)

    # Deserialize from bytes
    deserialized_user = User.deserialize(serialized)
    print("\nDeserialized User Model:")
    print(deserialized_user)


if __name__ == "__main__":
    main()
