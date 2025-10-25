"""
Test nested list of models serialization and deserialization functionality.
Based on examples/nested_list.py
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
    roles: list[Role]


class TestNestedListSerialization:
    """Test nested list of models serialization and deserialization functionality."""

    def test_user_with_nested_roles_list(self):
        """Test that a User model with nested Role list can be serialized and deserialized correctly."""
        user = User(
            user_id=123,
            username="admin",
            roles=[
                Role(role_id=1, role_name="admin"),
                Role(role_id=2, role_name="editor"),
                Role(role_id=3, role_name="user"),
            ],
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
        assert len(deserialized_user.roles) == len(user.roles)

        # Verify each role matches
        for i, role in enumerate(user.roles):
            assert deserialized_user.roles[i].role_id == role.role_id
            assert deserialized_user.roles[i].role_name == role.role_name

        # Verify the objects are equal
        assert deserialized_user == user

    def test_empty_roles_list(self):
        """Test serialization with an empty roles list."""
        user = User(user_id=1, username="test_user", roles=[])

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert deserialized.roles == []
        assert len(deserialized.roles) == 0

    def test_single_role_in_list(self):
        """Test serialization with a single role in the list."""
        user = User(
            user_id=1, username="test_user", roles=[Role(role_id=1, role_name="admin")]
        )

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert len(deserialized.roles) == 1
        assert deserialized.roles[0].role_id == 1
        assert deserialized.roles[0].role_name == "admin"

    def test_many_roles_in_list(self):
        """Test serialization with many roles in the list."""
        many_roles = [Role(role_id=i, role_name=f"role_{i}") for i in range(100)]
        user = User(user_id=1, username="test_user", roles=many_roles)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert len(deserialized.roles) == 100
        for i, role in enumerate(deserialized.roles):
            assert role.role_id == i
            assert role.role_name == f"role_{i}"

    def test_roles_with_special_characters(self):
        """Test serialization with roles containing special characters."""
        special_roles = [
            Role(role_id=1, role_name="admin@domain.com"),
            Role(role_id=2, role_name="user-with-dash"),
            Role(role_id=3, role_name="role_with_underscore"),
            Role(role_id=4, role_name="role with spaces"),
            Role(role_id=5, role_name="role/with/slashes"),
            Role(role_id=6, role_name="role\\with\\backslashes"),
            Role(role_id=7, role_name='role"with"quotes'),
            Role(role_id=8, role_name="role'with'apostrophes"),
            Role(role_id=9, role_name="role<with>brackets"),
            Role(role_id=10, role_name="role{with}braces"),
        ]

        user = User(user_id=1, username="test_user", roles=special_roles)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert len(deserialized.roles) == len(special_roles)
        for i, role in enumerate(deserialized.roles):
            assert role.role_id == special_roles[i].role_id
            assert role.role_name == special_roles[i].role_name

    def test_roles_with_unicode(self):
        """Test serialization with roles containing unicode characters."""
        unicode_roles = [
            Role(role_id=1, role_name="管理员"),  # Chinese
            Role(role_id=2, role_name="администратор"),  # Russian
            Role(role_id=3, role_name="administrateur"),  # French
            Role(role_id=4, role_name="管理者"),  # Japanese
            Role(role_id=5, role_name="مدير"),  # Arabic
            Role(role_id=6, role_name="🌍"),  # Emoji
            Role(role_id=7, role_name="café"),  # Accented characters
            Role(role_id=8, role_name="naïve"),  # Diaeresis
            Role(role_id=9, role_name="résumé"),  # Multiple accents
        ]

        user = User(user_id=1, username="test_user", roles=unicode_roles)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert len(deserialized.roles) == len(unicode_roles)
        for i, role in enumerate(deserialized.roles):
            assert role.role_id == unicode_roles[i].role_id
            assert role.role_name == unicode_roles[i].role_name

    def test_roles_with_edge_values(self):
        """Test serialization with roles containing edge case values."""
        edge_roles = [
            Role(role_id=0, role_name=""),  # Min values
            Role(role_id=255, role_name="a" * 1000),  # Max values
            Role(role_id=1, role_name=""),  # Mixed edge cases
            Role(role_id=0, role_name="admin"),
        ]

        user = User(user_id=1, username="test_user", roles=edge_roles)

        serialized = user.serialize()
        deserialized = User.deserialize(serialized)

        assert len(deserialized.roles) == len(edge_roles)
        for i, role in enumerate(deserialized.roles):
            assert role.role_id == edge_roles[i].role_id
            assert role.role_name == edge_roles[i].role_name

    def test_serialization_roundtrip_consistency(self):
        """Test that multiple serialization/deserialization cycles maintain data integrity."""
        user = User(
            user_id=42,
            username="roundtrip_test",
            roles=[
                Role(role_id=1, role_name="role1"),
                Role(role_id=2, role_name="role2"),
                Role(role_id=3, role_name="role3"),
            ],
        )

        # Perform multiple roundtrips
        current_user = user
        for _ in range(5):
            serialized = current_user.serialize()
            current_user = User.deserialize(serialized)

            assert current_user.user_id == user.user_id
            assert current_user.username == user.username
            assert len(current_user.roles) == len(user.roles)

            for i, role in enumerate(user.roles):
                assert current_user.roles[i].role_id == role.role_id
                assert current_user.roles[i].role_name == role.role_name

    def test_different_list_lengths(self):
        """Test serialization with different list lengths."""
        test_cases = [
            [],  # Empty list
            [Role(role_id=1, role_name="single")],  # Single item
            [
                Role(role_id=1, role_name="first"),
                Role(role_id=2, role_name="second"),
            ],  # Two items
            [Role(role_id=i, role_name=f"role_{i}") for i in range(5)],  # Five items
            [Role(role_id=i, role_name=f"role_{i}") for i in range(50)],  # Fifty items
        ]

        for roles in test_cases:
            user = User(user_id=1, username="test_user", roles=roles)

            serialized = user.serialize()
            deserialized = User.deserialize(serialized)

            assert len(deserialized.roles) == len(roles)
            for i, role in enumerate(roles):
                assert deserialized.roles[i].role_id == role.role_id
                assert deserialized.roles[i].role_name == role.role_name

    def test_nested_list_independence(self):
        """Test that nested lists maintain their independence."""
        roles1 = [Role(role_id=1, role_name="admin"), Role(role_id=2, role_name="user")]
        roles2 = [
            Role(role_id=3, role_name="guest"),
            Role(role_id=4, role_name="moderator"),
        ]

        user1 = User(user_id=1, username="user1", roles=roles1)
        user2 = User(user_id=2, username="user2", roles=roles2)

        # Serialize both users
        serialized1 = user1.serialize()
        serialized2 = user2.serialize()

        # Deserialize both users
        deserialized1 = User.deserialize(serialized1)
        deserialized2 = User.deserialize(serialized2)

        # Verify they maintain their separate identities
        assert len(deserialized1.roles) == 2
        assert deserialized1.roles[0].role_name == "admin"
        assert deserialized1.roles[1].role_name == "user"

        assert len(deserialized2.roles) == 2
        assert deserialized2.roles[0].role_name == "guest"
        assert deserialized2.roles[1].role_name == "moderator"

        # Verify they are not the same object
        assert deserialized1 != deserialized2

    def test_deeply_nested_lists(self):
        """Test serialization with deeply nested lists."""

        # Create a more complex nested structure
        class Permission(AnnotatedBaseModel):
            permission_id: Annotated[int, UInt8]
            permission_name: Annotated[str, String]

        class EnhancedRole(AnnotatedBaseModel):
            role_id: Annotated[int, UInt8]
            role_name: Annotated[str, String]
            permissions: list[Permission]

        class EnhancedUser(AnnotatedBaseModel):
            user_id: Annotated[int, UInt32]
            username: Annotated[str, String]
            roles: list[EnhancedRole]

        user = EnhancedUser(
            user_id=123,
            username="admin",
            roles=[
                EnhancedRole(
                    role_id=1,
                    role_name="admin",
                    permissions=[
                        Permission(permission_id=1, permission_name="read"),
                        Permission(permission_id=2, permission_name="write"),
                        Permission(permission_id=3, permission_name="delete"),
                    ],
                ),
                EnhancedRole(
                    role_id=2,
                    role_name="user",
                    permissions=[Permission(permission_id=1, permission_name="read")],
                ),
            ],
        )

        serialized = user.serialize()
        deserialized = EnhancedUser.deserialize(serialized)

        assert deserialized.user_id == 123
        assert deserialized.username == "admin"
        assert len(deserialized.roles) == 2

        # Check first role
        assert deserialized.roles[0].role_id == 1
        assert deserialized.roles[0].role_name == "admin"
        assert len(deserialized.roles[0].permissions) == 3
        assert deserialized.roles[0].permissions[0].permission_name == "read"
        assert deserialized.roles[0].permissions[1].permission_name == "write"
        assert deserialized.roles[0].permissions[2].permission_name == "delete"

        # Check second role
        assert deserialized.roles[1].role_id == 2
        assert deserialized.roles[1].role_name == "user"
        assert len(deserialized.roles[1].permissions) == 1
        assert deserialized.roles[1].permissions[0].permission_name == "read"
