"""
Test nested dict serialization and deserialization functionality with JSON.
Based on examples/nested_dict.py
"""

import datetime
from typing import Annotated

import pytest

from pybyntic import AnnotatedBaseModel
from pybyntic.types import DateTime32, StringJson, UInt32


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    created_at: Annotated[datetime.datetime, DateTime32]
    flags: Annotated[dict, StringJson]


class TestNestedDictSerialization:
    """Test nested dict serialization and deserialization functionality with JSON."""

    def test_user_with_nested_dict(self):
        """Test that a User model with nested dict can be serialized and deserialized correctly."""
        user = User(
            user_id=123,
            created_at=datetime.datetime.now(),
            flags={"is_admin": 1, "is_active": 1, "theme": 2},
        )

        # Serialize to bytes
        serialized = user.serialize()
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

        # Deserialize from bytes
        deserialized_user = User.deserialize(serialized)

        # Verify all fields match
        assert deserialized_user.user_id == user.user_id
        for key in user.flags:
            assert deserialized_user.flags[key] == user.flags[key]

    def test_empty_dict(self):
        """Test serialization with an empty dict."""
        user = User(user_id=1, created_at=datetime.datetime.now(), flags={})

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.flags == {}
        assert len(deserialized.flags) == 0

    def test_dict_with_different_value_types(self):
        """Test serialization with dict containing different value types."""
        test_cases = [
            {"is_admin": 1, "is_active": 0, "theme": 2},
            {"flag1": 100, "flag2": 200, "flag3": 300},
            {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
            {"single_key": 42},
        ]

        for flags in test_cases:
            user = User(user_id=1, created_at=datetime.datetime.now(), flags=flags)

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.flags == flags

    def test_dict_with_special_keys(self):
        """Test serialization with dict containing special characters in keys."""
        special_flags = {
            "is_admin@domain.com": 1,
            "user-with-dash": 2,
            "flag_with_underscore": 3,
            "flag with spaces": 4,
            "flag/with/slashes": 5,
            "flag\\with\\backslashes": 6,
            'flag"with"quotes': 7,
            "flag'with'apostrophes": 8,
            "flag<with>brackets": 9,
            "flag{with}braces": 10,
            "flag(with)parentheses": 11,
            "flag[with]square": 12,
            "flag|with|pipes": 13,
            "flag&with&ampersands": 14,
            "flag#with#hashes": 15,
            "flag%with%percent": 16,
            "flag+with+plus": 17,
            "flag=with=equals": 18,
            "flag?with?question": 19,
            "flag!with!exclamation": 20,
        }

        user = User(user_id=1, created_at=datetime.datetime.now(), flags=special_flags)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.flags == special_flags

    def test_dict_with_unicode_keys(self):
        """Test serialization with dict containing unicode characters in keys."""
        unicode_flags = {
            "管理员": 1,  # Chinese
            "администратор": 2,  # Russian
            "administrateur": 3,  # French
            "管理者": 4,  # Japanese
            "مدير": 5,  # Arabic
            "🌍": 6,  # Emoji
            "café": 7,  # Accented characters
            "naïve": 8,  # Diaeresis
            "résumé": 9,  # Multiple accents
        }

        user = User(user_id=1, created_at=datetime.datetime.now(), flags=unicode_flags)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.flags == unicode_flags

    def test_dict_with_large_values(self):
        """Test serialization with dict containing large integer values."""
        large_flags = {
            "max_int32": 2147483647,  # Max 32-bit signed int
            "min_int32": -2147483648,  # Min 32-bit signed int
            "max_uint32": 4294967295,  # Max 32-bit unsigned int
            "zero": 0,
            "negative": -100,
            "positive": 1000000,
        }

        user = User(user_id=1, created_at=datetime.datetime.now(), flags=large_flags)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.flags == large_flags

    def test_dict_with_many_keys(self):
        """Test serialization with dict containing many keys."""
        many_flags = {f"flag_{i}": i for i in range(1000)}

        user = User(user_id=1, created_at=datetime.datetime.now(), flags=many_flags)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.flags == many_flags
        assert len(deserialized.flags) == 1000

    def test_serialization_roundtrip_consistency(self):
        """Test that multiple serialization/deserialization cycles maintain data integrity."""
        user = User(
            user_id=42,
            created_at=datetime.datetime.now(),
            flags={"test_flag": 123, "another_flag": 456},
        )

        # Perform multiple roundtrips
        current_user = user
        for _ in range(5):
            serialized = current_user.serialize()
            current_user = User.deserialize(serialized)

            assert current_user.user_id == user.user_id
            assert current_user.flags == user.flags

    def test_datetime_serialization(self):
        """Test that datetime serialization works correctly with dict."""
        test_datetimes = [
            datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),  # Unix epoch
            datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),  # Y2K
            datetime.datetime(
                2024, 2, 29, 12, 30, 45, tzinfo=datetime.timezone.utc
            ),  # Leap year
            datetime.datetime.now(datetime.timezone.utc),  # Current time
        ]

        for test_datetime in test_datetimes:
            user = User(user_id=1, created_at=test_datetime, flags={"test": 1})

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.created_at.date() == test_datetime.date()
            assert deserialized.created_at.hour == test_datetime.hour
            assert deserialized.created_at.minute == test_datetime.minute
            # Note: DateTime32 may lose some precision, so we check up to minute level

    def test_nested_dict_independence(self):
        """Test that nested dicts maintain their independence."""
        flags1 = {"flag1": 1, "flag2": 2}
        flags2 = {"flag3": 3, "flag4": 4}

        user1 = User(user_id=1, created_at=datetime.datetime.now(), flags=flags1)
        user2 = User(user_id=2, created_at=datetime.datetime.now(), flags=flags2)

        # Serialize both users
        serialized1 = user1.serialize()
        serialized2 = user2.serialize()

        # Deserialize both users
        deserialized1 = User.deserialize(serialized1)
        deserialized2 = User.deserialize(serialized2)

        # Verify they maintain their separate identities
        assert deserialized1.flags == flags1
        assert deserialized2.flags == flags2

        # Verify they are not the same object
        assert deserialized1 != deserialized2

    def test_complex_nested_dict(self):
        """Test serialization with complex nested dict structures."""
        # Note: StringJson only supports JSON-serializable data, so we test with nested dicts
        complex_flags = {
            "user_settings": {"theme": "dark", "language": "en", "notifications": True},
            "permissions": {"read": 1, "write": 1, "delete": 0},
            "metadata": {
                "created_by": "admin",
                "version": 1,
                "tags": ["important", "user"],
            },
        }

        user = User(user_id=1, created_at=datetime.datetime.now(), flags=complex_flags)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.flags == complex_flags

    def test_dict_with_edge_values(self):
        """Test serialization with dict containing edge case values."""
        edge_flags = {
            "": 0,  # Empty string key
            "a": 0,  # Single character key
            "a" * 1000: 1000,  # Very long key
            "key_with_zero": 0,  # Zero value
            "key_with_negative": -1,  # Negative value
        }

        user = User(user_id=1, created_at=datetime.datetime.now(), flags=edge_flags)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.flags == edge_flags

    def test_back_compatibility(self):
        """
        Test deserialization of previously serialized data for backward compatibility.
        :return:
        """

        user = User(user_id=1,
                    created_at=datetime.datetime(2001, 1, 2, 3, 4,
                                                 tzinfo=datetime.timezone.utc),
                    flags={"foo": 1, "bar": 2})

        deserialized = User.deserialize(b'\x01\x00\x00\x00 EQ:\x14{"foo": 1, "bar": 2}')

        assert user.created_at.date() == deserialized.created_at.date()
        assert user.created_at.hour == deserialized.created_at.hour
        assert user.created_at.minute == deserialized.created_at.minute
        assert user.created_at.second == deserialized.created_at.second

        assert user.flags == deserialized.flags
        assert user.user_id == deserialized.user_id

                # assert deserialized == user
