"""
Test nested model serialization and deserialization functionality.
Based on examples/nested.py
"""

import pytest
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String, UInt8
from typing import Annotated


class Role(AnnotatedBaseModel):
    role_id: Annotated[int, UInt8]
    role_name: Annotated[str, String]


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    role: Role


class TestNestedSerialization:
    """Test nested model serialization and deserialization functionality."""

    def test_user_with_nested_role(self):
        """Test that a User model with nested Role can be serialized and deserialized correctly."""
        user = User(
            user_id=123, username="admin", role=Role(role_id=1, role_name="admin")
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
        assert deserialized_user.role.role_id == user.role.role_id
        assert deserialized_user.role.role_name == user.role.role_name

        # Verify the objects are equal
        assert deserialized_user == user

    def test_nested_role_with_different_values(self):
        """Test serialization with different role values."""
        test_cases = [
            {"role_id": 0, "role_name": ""},
            {"role_id": 255, "role_name": "super_admin"},  # Max UInt8
            {"role_id": 1, "role_name": "user"},
            {"role_id": 42, "role_name": "moderator"},
        ]

        for role_data in test_cases:
            user = User(user_id=1, username="test_user", role=Role(**role_data))

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.role.role_id == role_data["role_id"]
            assert deserialized.role.role_name == role_data["role_name"]

    def test_nested_role_with_special_characters(self):
        """Test serialization with role names containing special characters."""
        special_role_names = [
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

        for role_name in special_role_names:
            user = User(
                user_id=1,
                username="test_user",
                role=Role(role_id=1, role_name=role_name),
            )

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.role.role_name == role_name

    def test_nested_role_with_unicode(self):
        """Test serialization with role names containing unicode characters."""
        unicode_role_names = [
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

        for role_name in unicode_role_names:
            user = User(
                user_id=1,
                username="test_user",
                role=Role(role_id=1, role_name=role_name),
            )

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.role.role_name == role_name

    def test_serialization_roundtrip_consistency(self):
        """Test that multiple serialization/deserialization cycles maintain data integrity."""
        user = User(
            user_id=42,
            username="roundtrip_test",
            role=Role(role_id=5, role_name="test_role"),
        )

        # Perform multiple roundtrips
        current_user = user
        for _ in range(5):
            serialized = current_user.serialize()
            current_user = User.deserialize(serialized)

            assert current_user.user_id == user.user_id
            assert current_user.username == user.username
            assert current_user.role.role_id == user.role.role_id
            assert current_user.role.role_name == user.role.role_name

    def test_nested_model_independence(self):
        """Test that nested models maintain their independence."""
        role1 = Role(role_id=1, role_name="admin")
        role2 = Role(role_id=2, role_name="user")

        user1 = User(user_id=1, username="user1", role=role1)
        user2 = User(user_id=2, username="user2", role=role2)

        # Serialize both users
        serialized1 = user1.serialize()
        serialized2 = user2.serialize()

        # Deserialize both users
        deserialized1 = User.deserialize(serialized1)
        deserialized2 = User.deserialize(serialized2)

        # Verify they maintain their separate identities
        assert deserialized1.role.role_id == 1
        assert deserialized1.role.role_name == "admin"
        assert deserialized2.role.role_id == 2
        assert deserialized2.role.role_name == "user"

        # Verify they are not the same object
        assert deserialized1 != deserialized2

    def test_deeply_nested_models(self):
        """Test serialization with deeply nested models."""
        # Create a more complex nested structure
        class Permission(AnnotatedBaseModel):
            permission_id: Annotated[int, UInt8]
            permission_name: Annotated[str, String]

        class EnhancedRole(AnnotatedBaseModel):
            role_id: Annotated[int, UInt8]
            role_name: Annotated[str, String]
            permission: Permission

        class EnhancedUser(AnnotatedBaseModel):
            user_id: Annotated[int, UInt32]
            username: Annotated[str, String]
            role: EnhancedRole

        user = EnhancedUser(
            user_id=123,
            username="admin",
            role=EnhancedRole(
                role_id=1,
                role_name="admin",
                permission=Permission(permission_id=1, permission_name="full_access"),
            ),
        )

        serialized = user.serialize()
        deserialized = EnhancedUser.deserialize(serialized)

        assert deserialized.user_id == 123
        assert deserialized.username == "admin"
        assert deserialized.role.role_id == 1
        assert deserialized.role.role_name == "admin"
        assert deserialized.role.permission.permission_id == 1
        assert deserialized.role.permission.permission_name == "full_access"

    def test_nested_model_with_edge_values(self):
        """Test nested models with edge case values."""
        edge_cases = [
            # Min values
            {"role_id": 0, "role_name": ""},
            # Max values
            {"role_id": 255, "role_name": "a" * 1000},
            # Mixed edge cases
            {"role_id": 1, "role_name": ""},
            {"role_id": 0, "role_name": "admin"},
        ]

        for role_data in edge_cases:
            user = User(user_id=1, username="test_user", role=Role(**role_data))

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert deserialized.role.role_id == role_data["role_id"]
            assert deserialized.role.role_name == role_data["role_name"]
