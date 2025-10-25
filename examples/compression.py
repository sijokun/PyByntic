"""
You can use custom encoder and decoder functions to compress the serialized data of a PyByntic model.
"""

import datetime
import zlib
from typing import Annotated

from pybyntic import AnnotatedBaseModel
from pybyntic.types import Bool, Date, String, UInt32


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]


def main():
    user = User(
        user_id=123, username="admin", is_active=True, join_date=datetime.date.today()
    )

    print("Original User Model:")
    print(user)

    # Serialize to bytes
    serialized = user.serialize(encoder=zlib.compress)
    print("\nSerialized Bytes:")
    print(serialized)

    # Deserialize from bytes
    deserialized_user = User.deserialize(serialized, decoder=zlib.decompress)
    print("\nDeserialized User Model:")
    print(deserialized_user)


if __name__ == "__main__":
    main()
