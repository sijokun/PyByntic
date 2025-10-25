"""
Test list serialization and deserialization functionality.
Based on examples/list.py
"""

import pytest
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String
from typing import Annotated


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    roles: Annotated[list[str], list[String]]


class TestListSerialization:
    """Test list serialization and deserialization functionality."""

    def test_user_with_roles_serialization(self):
        """Test that a User model with roles list can be serialized and deserialized correctly."""
        user = User(user_id=123, username="admin", roles=["admin", "editor", "user"])

        # Serialize to bytes
        serialized = user.serialize()
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

        # Deserialize from bytes
        deserialized_user = User.deserialize(serialized)

        # Verify all fields match
        assert deserialized_user.user_id == user.user_id
        assert deserialized_user.username == user.username
        assert deserialized_user.roles == user.roles

        # Verify the objects are equal
        assert deserialized_user == user

    def test_empty_roles_list(self):
        """Test serialization with an empty roles list."""
        user = User(user_id=1, username="test_user", roles=[])

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.roles == []
        assert len(deserialized.roles) == 0

    def test_single_role(self):
        """Test serialization with a single role."""
        user = User(user_id=1, username="test_user", roles=["admin"])

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.roles == ["admin"]
        assert len(deserialized.roles) == 1

    def test_many_roles(self):
        """Test serialization with many roles."""
        many_roles = [f"role_{i}" for i in range(100)]
        user = User(user_id=1, username="test_user", roles=many_roles)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.roles == many_roles
        assert len(deserialized.roles) == 100

    def test_roles_with_special_characters(self):
        """Test serialization with roles containing special characters."""
        special_roles = [
            "admin@domain.com",
            "user-with-dash",
            "role_with_underscore",
            "role with spaces",
            "role/with/slashes",
            "role\\with\\backslashes",
            'role"with"quotes',
            "role'with'apostrophes",
            "role<with>brackets",
            "role{with}braces",
            "role(with)parentheses",
            "role[with]square",
            "role|with|pipes",
            "role&with&ampersands",
            "role#with#hashes",
            "role%with%percent",
            "role+with+plus",
            "role=with=equals",
            "role?with?question",
            "role!with!exclamation",
        ]

        user = User(user_id=1, username="test_user", roles=special_roles)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.roles == special_roles

    def test_roles_with_unicode(self):
        """Test serialization with roles containing unicode characters."""
        unicode_roles = [
            "管理员",  # Chinese
            "администратор",  # Russian
            "administrateur",  # French
            "管理者",  # Japanese
            "مدير",  # Arabic
            "🌍",  # Emoji
            "café",  # Accented characters
            "naïve",  # Diaeresis
            "résumé",  # Multiple accents
        ]

        user = User(user_id=1, username="test_user", roles=unicode_roles)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.roles == unicode_roles

    def test_roles_with_empty_strings(self):
        """Test serialization with roles containing empty strings."""
        roles_with_empty = ["admin", "", "user", "", "guest"]

        user = User(user_id=1, username="test_user", roles=roles_with_empty)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.roles == roles_with_empty

    def test_serialization_roundtrip_consistency(self):
        """Test that multiple serialization/deserialization cycles maintain data integrity."""
        user = User(
            user_id=42, username="roundtrip_test", roles=["role1", "role2", "role3"]
        )

        # Perform multiple roundtrips
        current_user = user
        for _ in range(5):
            serialized = current_user.serialize()
            current_user = User.deserialize(serialized)

            assert current_user.user_id == user.user_id
            assert current_user.username == user.username
            assert current_user.roles == user.roles

    def test_different_list_lengths(self):
        """Test serialization with different list lengths."""
        test_cases = [
            [],  # Empty list
            ["single"],  # Single item
            ["first", "second"],  # Two items
            ["a", "b", "c", "d", "e"],  # Five items
            [f"item_{i}" for i in range(50)],  # Fifty items
        ]

        for roles in test_cases:
            user = User(user_id=1, username="test_user", roles=roles)

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.roles == roles
            assert len(deserialized.roles) == len(roles)
