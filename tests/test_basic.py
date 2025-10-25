"""
Test basic serialization and deserialization functionality.
Based on examples/basic.py
"""

import datetime
from typing import Annotated

import pytest

from pybyntic import AnnotatedBaseModel
from pybyntic.types import Bool, Date, String, UInt32


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]


class TestBasicSerialization:
    """Test basic serialization and deserialization functionality."""

    def test_user_serialization_deserialization(self):
        """Test that a User model can be serialized and deserialized correctly."""
        # Create a user instance
        user = User(
            user_id=123,
            username="admin",
            is_active=True,
            join_date=datetime.date.today(),
        )

        # Serialize to bytes
        serialized = user.serialize()
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

        # Deserialize from bytes
        deserialized_user = User.deserialize(serialized)

        # Verify all fields match
        assert deserialized_user.user_id == user.user_id
        assert deserialized_user.username == user.username
        assert deserialized_user.is_active == user.is_active
        assert deserialized_user.join_date == user.join_date

        # Verify the objects are equal
        assert deserialized_user == user

    def test_user_with_different_values(self):
        """Test serialization with different user values."""
        test_cases = [
            {
                "user_id": 0,
                "username": "",
                "is_active": False,
                "join_date": datetime.date(1970, 1, 1),
            },
            {
                "user_id": 4294967295,  # Max UInt32
                "username": "a" * 1000,  # Long string
                "is_active": True,
                "join_date": datetime.date(2024, 12, 31),
            },
            {
                "user_id": 1,
                "username": "test_user",
                "is_active": False,
                "join_date": datetime.date(2000, 6, 15),
            },
        ]

        for case in test_cases:
            user = User(**case)
            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.user_id == case["user_id"]
            assert deserialized.username == case["username"]
            assert deserialized.is_active == case["is_active"]
            assert deserialized.join_date == case["join_date"]

    def test_serialization_roundtrip_consistency(self):
        """Test that multiple serialization/deserialization cycles maintain data integrity."""
        user = User(
            user_id=42,
            username="roundtrip_test",
            is_active=True,
            join_date=datetime.date(2023, 1, 1),
        )

        # Perform multiple roundtrips
        current_user = user
        for _ in range(5):
            serialized = current_user.serialize()
            current_user = User.deserialize(serialized)

            assert current_user.user_id == user.user_id
            assert current_user.username == user.username
            assert current_user.is_active == user.is_active
            assert current_user.join_date == user.join_date

    def test_empty_string_handling(self):
        """Test that empty strings are handled correctly."""
        user = User(
            user_id=1,
            username="",  # Empty string
            is_active=True,
            join_date=datetime.date.today(),
        )

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.username == ""

    def test_boolean_values(self):
        """Test both True and False boolean values."""
        for is_active in [True, False]:
            user = User(
                user_id=1,
                username="test",
                is_active=is_active,
                join_date=datetime.date.today(),
            )

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.is_active == is_active

    def test_date_edge_cases(self):
        """Test date serialization with edge cases."""
        edge_dates = [
            datetime.date(1970, 1, 1),  # Unix epoch
            datetime.date(2000, 1, 1),  # Y2K
            datetime.date(2024, 2, 29),  # Leap year
            datetime.date(2038, 1, 19),  # Near 32-bit time limit
        ]

        for test_date in edge_dates:
            user = User(user_id=1, username="test", is_active=True, join_date=test_date)

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.join_date == test_date
