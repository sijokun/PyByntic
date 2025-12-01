import pytest
from typing import Annotated
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String, DateTime32
from datetime import datetime


def test_backward_compatibility_string():
    # V1 Model
    class UserV1(AnnotatedBaseModel):
        user_id: Annotated[int, UInt32]
        username: Annotated[str, String]

    # V2 Model with an extra field at the end
    class UserV2(AnnotatedBaseModel):
        user_id: Annotated[int, UInt32]
        username: Annotated[str, String]
        email: Annotated[str, String]

    # Create V1 data
    user_v1 = UserV1(user_id=123, username="test_user")
    serialized_v1 = user_v1.serialize()

    # Try to deserialize V1 data with V2 model
    # This is expected to fail currently
    user_v2 = UserV2.deserialize(serialized_v1)
    assert user_v2.email == ""


def test_backward_compatibility_integer():
    # V1 Model
    class UserV1(AnnotatedBaseModel):
        user_id: Annotated[int, UInt32]
        datetime: Annotated[datetime, DateTime32]

    # V2 Model with an extra field at the end
    class UserV2(AnnotatedBaseModel):
        user_id: Annotated[int, UInt32]
        datetime: Annotated[datetime, DateTime32]
        likes: Annotated[int, UInt32]

    # Create V1 data
    user_v1 = UserV1(user_id=123, datetime=datetime.now())
    serialized_v1 = user_v1.serialize()

    # Try to deserialize V1 data with V2 model
    # This is expected to fail currently
    user_v2 = UserV2.deserialize(serialized_v1)
    assert user_v2.likes == 0
