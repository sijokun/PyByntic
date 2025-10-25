"""
PyByntic supports serialization and deserialization of nested models.
"""

from typing import Annotated

from pybyntic import AnnotatedBaseModel
from pybyntic.types import String, UInt8, UInt32


class Role(AnnotatedBaseModel):
    role_id: Annotated[int, UInt8]
    role_name: Annotated[str, String]


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    role: Role


def main():
    user = User(user_id=123, username="admin", role=Role(role_id=1, role_name="admin"))

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
