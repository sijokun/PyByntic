"""
PyByntic supports serialization and deserialization of nested dicts as JSON.
"""

from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, DateTime32, StringJson
from typing import Annotated

import datetime


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    created_at: Annotated[datetime.datetime, DateTime32]
    flags: Annotated[dict[str, int], StringJson]


def main():
    user = User(
        user_id=123,
        created_at=datetime.datetime.now(),
        flags={"is_admin": 1, "is_active": 1, "theme": 2},
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
