"""
Example demonstrating the use of Nullable type with PyByntic.
Nullable adds one extra byte to indicate if the value is null.
If you want to reduce the size, consider using default values instead.
"""
from typing import Annotated, Optional

from pybyntic import AnnotatedBaseModel
from pybyntic.types import Nullable, String, UInt32


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[Optional[str], Nullable[String]]


def print_example(user):
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


def main():
    user_a = User(user_id=123, username="admin")
    print("Example with username:")
    print_example(user_a)
    print("-----------------------------------")
    print("\nExample with null username:")
    user_b = User(user_id=456, username=None)
    print_example(user_b)


if __name__ == "__main__":
    main()
