"""
Test custom encoder and decoder functionality.
Based on examples/compression.py
"""

import datetime
import pytest
import zlib
import gzip
import bz2
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String, Bool, Date
from typing import Annotated


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]


class TestCompressionSerialization:
    """Test custom encoder and decoder functionality."""

    def test_user_with_zlib_compression(self):
        """Test that a User model can be serialized and deserialized with zlib compression."""
        user = User(
            user_id=123,
            username="admin",
            is_active=True,
            join_date=datetime.date.today(),
        )

        # Serialize to bytes with zlib compression
        serialized = user.serialize(encoder=zlib.compress)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

        # Deserialize from bytes with zlib decompression
        deserialized_user = User.deserialize(serialized, decoder=zlib.decompress)

        # Verify all fields match
        assert deserialized_user.user_id == user.user_id
        assert deserialized_user.username == user.username
        assert deserialized_user.is_active == user.is_active
        assert deserialized_user.join_date == user.join_date

        # Verify the objects are equal
        assert deserialized_user == user

    def test_compression_size_reduction(self):
        """Test that compression actually reduces the size of serialized data."""
        # Create a user with a long username to make compression more effective
        user = User(
            user_id=123,
            username="admin" * 100,  # Long string for better compression
            is_active=True,
            join_date=datetime.date.today(),
        )

        # Serialize without compression
        serialized_uncompressed = user.serialize()

        # Serialize with zlib compression
        serialized_compressed = user.serialize(encoder=zlib.compress)

        # Verify compression reduces size
        assert len(serialized_compressed) < len(serialized_uncompressed)

        # Verify both can be deserialized correctly
        deserialized_uncompressed = User.deserialize(serialized_uncompressed)
        deserialized_compressed = User.deserialize(
            serialized_compressed, decoder=zlib.decompress
        )

        assert deserialized_uncompressed == deserialized_compressed
        assert deserialized_compressed == user

    def test_gzip_compression(self):
        """Test serialization with gzip compression."""
        user = User(
            user_id=456,
            username="test_user",
            is_active=False,
            join_date=datetime.date(2023, 1, 1),
        )

        # Serialize with gzip compression
        serialized = user.serialize(encoder=gzip.compress)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

        # Deserialize with gzip decompression
        deserialized_user = User.deserialize(serialized, decoder=gzip.decompress)

        # Verify all fields match
        assert deserialized_user.user_id == user.user_id
        assert deserialized_user.username == user.username
        assert deserialized_user.is_active == user.is_active
        assert deserialized_user.join_date == user.join_date

    def test_bz2_compression(self):
        """Test serialization with bz2 compression."""
        user = User(
            user_id=789,
            username="bz2_test",
            is_active=True,
            join_date=datetime.date(2024, 6, 15),
        )

        # Serialize with bz2 compression
        serialized = user.serialize(encoder=bz2.compress)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

        # Deserialize with bz2 decompression
        deserialized_user = User.deserialize(serialized, decoder=bz2.decompress)

        # Verify all fields match
        assert deserialized_user.user_id == user.user_id
        assert deserialized_user.username == user.username
        assert deserialized_user.is_active == user.is_active
        assert deserialized_user.join_date == user.join_date

    def test_custom_encoder_decoder(self):
        """Test serialization with custom encoder/decoder functions."""

        def custom_encoder(data):
            # Simple XOR encoding
            key = 0x42
            return bytes(b ^ key for b in data)

        def custom_decoder(data):
            # Simple XOR decoding
            key = 0x42
            return bytes(b ^ key for b in data)

        user = User(
            user_id=999,
            username="custom_test",
            is_active=True,
            join_date=datetime.date.today(),
        )

        # Serialize with custom encoder
        serialized = user.serialize(encoder=custom_encoder)
        assert isinstance(serialized, bytes)
        assert len(serialized) > 0

        # Deserialize with custom decoder
        deserialized_user = User.deserialize(serialized, decoder=custom_decoder)

        # Verify all fields match
        assert deserialized_user.user_id == user.user_id
        assert deserialized_user.username == user.username
        assert deserialized_user.is_active == user.is_active
        assert deserialized_user.join_date == user.join_date

    def test_encoder_without_decoder_raises_error(self):
        """Test that deserializing compressed data without decoder raises an error."""
        user = User(
            user_id=123,
            username="admin",
            is_active=True,
            join_date=datetime.date.today(),
        )

        # Serialize with compression
        serialized = user.serialize(encoder=zlib.compress)

        # Try to deserialize without decoder - should raise an error
        with pytest.raises(Exception):
            User.deserialize(serialized)

    def test_decoder_without_encoder_raises_error(self):
        """Test that deserializing uncompressed data with decoder raises an error."""
        user = User(
            user_id=123,
            username="admin",
            is_active=True,
            join_date=datetime.date.today(),
        )

        # Serialize without compression
        serialized = user.serialize()

        # Deserialize with decoder - should raise an error
        with pytest.raises(zlib.error):
            User.deserialize(serialized, decoder=zlib.decompress)

    def test_serialization_roundtrip_consistency_with_compression(self):
        """Test that multiple serialization/deserialization cycles maintain data integrity with compression."""
        user = User(
            user_id=42,
            username="roundtrip_test",
            is_active=True,
            join_date=datetime.date(2023, 1, 1),
        )

        # Perform multiple roundtrips with compression
        current_user = user
        for _ in range(5):
            serialized = current_user.serialize(encoder=zlib.compress)
            current_user = User.deserialize(serialized, decoder=zlib.decompress)

            assert current_user.user_id == user.user_id
            assert current_user.username == user.username
            assert current_user.is_active == user.is_active
            assert current_user.join_date == user.join_date

    def test_different_compression_algorithms(self):
        """Test serialization with different compression algorithms."""
        user = User(
            user_id=123,
            username="compression_test" * 50,  # Long string for better compression
            is_active=True,
            join_date=datetime.date.today(),
        )

        # Test different compression algorithms
        compression_algorithms = [
            (zlib.compress, zlib.decompress),
            (gzip.compress, gzip.decompress),
            (bz2.compress, bz2.decompress),
        ]

        for encoder, decoder in compression_algorithms:
            serialized = user.serialize(encoder=encoder)
            deserialized = User.deserialize(serialized, decoder=decoder)

            assert deserialized.user_id == user.user_id
            assert deserialized.username == user.username
            assert deserialized.is_active == user.is_active
            assert deserialized.join_date == user.join_date

    def test_compression_with_edge_cases(self):
        """Test compression with edge case values."""
        edge_cases = [
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

        for case in edge_cases:
            user = User(**case)
            serialized = user.serialize(encoder=zlib.compress)
            deserialized = User.deserialize(serialized, decoder=zlib.decompress)

            assert deserialized.user_id == case["user_id"]
            assert deserialized.username == case["username"]
            assert deserialized.is_active == case["is_active"]
            assert deserialized.join_date == case["join_date"]

    def test_compression_with_unicode(self):
        """Test compression with unicode characters."""
        unicode_usernames = [
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

        for username in unicode_usernames:
            user = User(
                user_id=1,
                username=username,
                is_active=True,
                join_date=datetime.date.today(),
            )

            serialized = user.serialize(encoder=zlib.compress)
            deserialized = User.deserialize(serialized, decoder=zlib.decompress)

            assert deserialized.username == username

    def test_compression_independence(self):
        """Test that compression maintains independence between different users."""
        user1 = User(
            user_id=1, username="user1", is_active=True, join_date=datetime.date.today()
        )

        user2 = User(
            user_id=2,
            username="user2",
            is_active=False,
            join_date=datetime.date(2023, 1, 1),
        )

        # Serialize both users with compression
        serialized1 = user1.serialize(encoder=zlib.compress)
        serialized2 = user2.serialize(encoder=zlib.compress)

        # Deserialize both users
        deserialized1 = User.deserialize(serialized1, decoder=zlib.decompress)
        deserialized2 = User.deserialize(serialized2, decoder=zlib.decompress)

        # Verify they maintain their separate identities
        assert deserialized1.user_id == 1
        assert deserialized1.username == "user1"
        assert deserialized1.is_active == True

        assert deserialized2.user_id == 2
        assert deserialized2.username == "user2"
        assert deserialized2.is_active == False

        # Verify they are not the same object
        assert deserialized1 != deserialized2
