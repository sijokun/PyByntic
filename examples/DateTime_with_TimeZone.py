"""
Example demonstrating using DateTime field that includes timezone.
This example defines a User model with a DateTime64TZ field for storing,
DateTime32TZ also could be used for timezone-aware datetime values with less precision.

TimeZone is saved as minutes offset from UTC, not as a named timezone.
This means that during deserialization, the exact timezone name (like "America/New_York") is not preserved,
but the correct UTC offset is maintained. With winter time changes, the offset may vary.
Save utc time and user's timezone separately if you need to preserve the exact timezone.

"""

import datetime
from typing import Annotated

from pybyntic import AnnotatedBaseModel
from pybyntic.types import Bool, DateTime64TZ, String, UInt32
import zoneinfo


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    created_at: Annotated[datetime.datetime, DateTime64TZ[3]]


def main():
    created_at = datetime.datetime.now().astimezone(zoneinfo.ZoneInfo("America/New_York"))
    user = User(
        user_id=123, username="admin", is_active=True, created_at=created_at
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
