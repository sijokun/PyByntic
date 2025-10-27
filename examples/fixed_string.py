"""
Example demonstrating the use of FixedString type.

:param int length: Length of the fixed string in bytes.
:param int encoding: Optional string encoding (default is "utf-8").

Recommended to use fixed-byte length encodings for FixedString. For example, "UTF-16LE" that uses 2 bytes per character.

Example of when FixedString is useful: language codes, ISO country codes, currency codes, etc.

If string is shorter than the fixed length, it will be padded with null bytes.
If string is longer than the fixed length, it will be truncated.
"""
from typing import Annotated

from pybyntic import AnnotatedBaseModel
from pybyntic.types import String, UInt32, FixedString


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    language: Annotated[str, FixedString[2]]
    country: Annotated[str, FixedString[4, "UTF-16LE"]]


def main():
    user = User(
        user_id=123, username="admin", language="NE"
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
