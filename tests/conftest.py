"""
Shared fixtures and test configuration for PyByntic tests.
"""

import datetime
import random
from typing import Annotated

import pytest

from pybyntic import AnnotatedBaseModel
from pybyntic.types import Bool, Date, DateTime32, String, StringJson, UInt8, UInt32


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]


class Role(AnnotatedBaseModel):
    role_id: Annotated[int, UInt8]
    role_name: Annotated[str, String]


class UserWithRole(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    role: Role


class UserWithRoles(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    roles: list[Role]


class UserWithDict(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    created_at: Annotated[datetime.datetime, DateTime32]
    flags: Annotated[dict[str, int], StringJson]


@pytest.fixture
def sample_user():
    """Fixture providing a sample User instance."""
    return User(
        user_id=123,
        username="test_user",
        is_active=True,
        join_date=datetime.date.today(),
    )


@pytest.fixture
def sample_role():
    """Fixture providing a sample Role instance."""
    return Role(role_id=1, role_name="admin")


@pytest.fixture
def sample_user_with_role():
    """Fixture providing a sample UserWithRole instance."""
    return UserWithRole(
        user_id=123, username="test_user", role=Role(role_id=1, role_name="admin")
    )


@pytest.fixture
def sample_user_with_roles():
    """Fixture providing a sample UserWithRoles instance."""
    return UserWithRoles(
        user_id=123,
        username="test_user",
        roles=[
            Role(role_id=1, role_name="admin"),
            Role(role_id=2, role_name="editor"),
            Role(role_id=3, role_name="user"),
        ],
    )


@pytest.fixture
def sample_user_with_dict():
    """Fixture providing a sample UserWithDict instance."""
    return UserWithDict(
        user_id=123,
        created_at=datetime.datetime.now(datetime.timezone.utc),
        flags={"is_admin": 1, "is_active": 1, "theme": 2},
    )


@pytest.fixture
def edge_case_user():
    """Fixture providing a User instance with edge case values."""
    return User(
        user_id=0, username="", is_active=False, join_date=datetime.date(1970, 1, 1)
    )


@pytest.fixture
def max_value_user():
    """Fixture providing a User instance with maximum values."""
    return User(
        user_id=4294967295,  # Max UInt32
        username="a" * 1000,  # Long string
        is_active=True,
        join_date=datetime.date(2024, 12, 31),
    )


@pytest.fixture
def unicode_user():
    """Fixture providing a User instance with unicode characters."""
    return User(
        user_id=1,
        username="管理员",  # Chinese characters
        is_active=True,
        join_date=datetime.date.today(),
    )


@pytest.fixture
def random_user():
    """Fixture providing a randomly generated User instance."""
    random.seed(42)  # For reproducible tests
    return User(
        user_id=random.randint(0, 1000000),
        username=f"user_{random.randint(1000, 9999)}",
        is_active=random.choice([True, False]),
        join_date=datetime.date(
            random.randint(1970, 2024), random.randint(1, 12), random.randint(1, 28)
        ),
    )


@pytest.fixture
def test_strings():
    """Fixture providing various test strings."""
    return [
        "",  # Empty string
        "a",  # Single character
        "hello world",  # Regular string
        "a" * 1000,  # Long string
        "Hello, 世界!",  # Unicode string
        "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",  # Special characters
        "\\n\\t\\r",  # Escape characters
        "🌍",  # Emoji
        "café",  # Accented characters
        "naïve",  # Diaeresis
        "résumé",  # Multiple accents
    ]


@pytest.fixture
def test_integers():
    """Fixture providing various test integers."""
    return [
        0,
        1,
        -1,
        127,  # Max Int8
        -128,  # Min Int8
        255,  # Max UInt8
        32767,  # Max Int16
        -32768,  # Min Int16
        65535,  # Max UInt16
        2147483647,  # Max Int32
        -2147483648,  # Min Int32
        4294967295,  # Max UInt32
        9223372036854775807,  # Max Int64
        -9223372036854775808,  # Min Int64
        18446744073709551615,  # Max UInt64
    ]


@pytest.fixture
def test_floats():
    """Fixture providing various test floats."""
    return [
        0.0,
        1.0,
        -1.0,
        3.14159,
        -3.14159,
        1.23456789,
        3.4028235e38,  # Max Float32
        -3.4028235e38,  # Min Float32
        1.7976931348623157e308,  # Max Float64
        -1.7976931348623157e308,  # Min Float64
    ]


@pytest.fixture
def test_dates():
    """Fixture providing various test dates."""
    return [
        datetime.date(1970, 1, 1),  # Unix epoch
        datetime.date(2000, 1, 1),  # Y2K
        datetime.date(2024, 2, 29),  # Leap year
        datetime.date.today(),  # Today
        datetime.date(2038, 1, 19),  # Near 32-bit time limit
    ]


@pytest.fixture
def test_datetimes():
    """Fixture providing various test datetimes."""
    return [
        datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),  # Unix epoch
        datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),  # Y2K
        datetime.datetime(
            2024, 2, 29, 12, 30, 45, tzinfo=datetime.timezone.utc
        ),  # Leap year
        datetime.datetime.now(datetime.timezone.utc),  # Current time
    ]


@pytest.fixture
def test_dicts():
    """Fixture providing various test dictionaries."""
    return [
        {},  # Empty dict
        {"key": "value"},  # Simple dict
        {"nested": {"key": "value"}},  # Nested dict
        {"list": [1, 2, 3]},  # Dict with list
        {"string": "hello", "number": 42, "boolean": True},  # Mixed types
        {"unicode": "世界", "emoji": "🌍"},  # Unicode
        {"special": "!@#$%^&*()_+-=[]{}|;':\",./<>?"},  # Special characters
    ]


@pytest.fixture
def compression_algorithms():
    """Fixture providing compression algorithm pairs."""
    import bz2
    import gzip
    import zlib

    return [
        (zlib.compress, zlib.decompress),
        (gzip.compress, gzip.decompress),
        (bz2.compress, bz2.decompress),
    ]


@pytest.fixture(scope="session")
def random_seed():
    """Fixture to set random seed for reproducible tests."""
    random.seed(42)
    return 42


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "benchmark: marks tests as benchmark tests")
    config.addinivalue_line("markers", "compression: marks tests as compression tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add slow marker to benchmark tests
        if "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.benchmark)

        # Add compression marker to compression tests
        if "compression" in item.nodeid:
            item.add_marker(pytest.mark.compression)

        # Add slow marker to tests with large data structures
        if "large" in item.name or "many" in item.name:
            item.add_marker(pytest.mark.slow)
