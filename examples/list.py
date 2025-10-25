"""
PyByntic supports serialization and deserialization of models containing lists
"""

from typing import Annotated

from pybyntic import AnnotatedBaseModel
from pybyntic.types import String, UInt32


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    roles: Annotated[list[str], list[String]]


def main():
    user = User(user_id=123, username="admin", roles=["admin", "editor", "user"])

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
