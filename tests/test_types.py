"""
Test individual type serialization and deserialization functionality.
Tests all the types defined in byto.types module.
"""

import datetime
from typing import Annotated

import pytest

from pybyntic import AnnotatedBaseModel
from pybyntic.types import (
    Bool,
    Date,
    DateTime32,
    DateTime64,
    Float32,
    Float64,
    Int8,
    Int16,
    Int32,
    Int64,
    Skip,
    String,
    StringJson,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    UInt128,
)


class TestIndividualTypes:
    """Test individual type serialization and deserialization functionality."""

    def test_skip_type(self):
        """Test Skip type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            field1: Annotated[int, UInt32]
            skipped_field: Annotated[str, Skip] = "default_value"
            field2: Annotated[str, String]

        model = TestModel(
            field1=123, skipped_field="this should be skipped", field2="test"
        )

        serialized = model.serialize()
        deserialized = TestModel.deserialize(serialized)

        assert deserialized.field1 == 123
        assert deserialized.field2 == "test"
        assert deserialized.skipped_field == "default_value"  # Should get default value

    def test_bool_type(self):
        """Test Bool type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            bool_field: Annotated[bool, Bool]

        test_cases = [True, False]

        for value in test_cases:
            model = TestModel(bool_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.bool_field == value

    def test_int8_type(self):
        """Test Int8 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            int8_field: Annotated[int, Int8]

        test_cases = [-128, -1, 0, 1, 127]  # Int8 range

        for value in test_cases:
            model = TestModel(int8_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.int8_field == value

    def test_int16_type(self):
        """Test Int16 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            int16_field: Annotated[int, Int16]

        test_cases = [-32768, -1, 0, 1, 32767]  # Int16 range

        for value in test_cases:
            model = TestModel(int16_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.int16_field == value

    def test_int32_type(self):
        """Test Int32 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            int32_field: Annotated[int, Int32]

        test_cases = [-2147483648, -1, 0, 1, 2147483647]  # Int32 range

        for value in test_cases:
            model = TestModel(int32_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.int32_field == value

    def test_int64_type(self):
        """Test Int64 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            int64_field: Annotated[int, Int64]

        test_cases = [
            -9223372036854775808,
            -1,
            0,
            1,
            9223372036854775807,
        ]  # Int64 range

        for value in test_cases:
            model = TestModel(int64_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.int64_field == value

    def test_uint8_type(self):
        """Test UInt8 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            uint8_field: Annotated[int, UInt8]

        test_cases = [0, 1, 127, 128, 255]  # UInt8 range

        for value in test_cases:
            model = TestModel(uint8_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.uint8_field == value

    def test_uint16_type(self):
        """Test UInt16 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            uint16_field: Annotated[int, UInt16]

        test_cases = [0, 1, 32767, 32768, 65535]  # UInt16 range

        for value in test_cases:
            model = TestModel(uint16_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.uint16_field == value

    def test_uint32_type(self):
        """Test UInt32 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            uint32_field: Annotated[int, UInt32]

        test_cases = [0, 1, 2147483647, 2147483648, 4294967295]  # UInt32 range

        for value in test_cases:
            model = TestModel(uint32_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.uint32_field == value

    def test_uint64_type(self):
        """Test UInt64 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            uint64_field: Annotated[int, UInt64]

        test_cases = [
            0,
            1,
            9223372036854775807,
            9223372036854775808,
            18446744073709551615,
        ]  # UInt64 range

        for value in test_cases:
            model = TestModel(uint64_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.uint64_field == value

    def test_float32_type(self):
        """Test Float32 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            float32_field: Annotated[float, Float32]

        test_cases = [0.0, 1.0, -1.0, 3.14159, -3.14159, 1.23456789]

        for value in test_cases:
            model = TestModel(float32_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            # Float32 has limited precision, so we check approximate equality
            assert abs(deserialized.float32_field - value) < 1e-6

    def test_float64_type(self):
        """Test Float64 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            float64_field: Annotated[float, Float64]

        test_cases = [
            0.0,
            1.0,
            -1.0,
            3.141592653589793,
            -3.141592653589793,
            1.234567890123456789,
        ]

        for value in test_cases:
            model = TestModel(float64_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            # Float64 has higher precision, so we check approximate equality
            assert abs(deserialized.float64_field - value) < 1e-15

    def test_uint128_type(self):
        """Test UInt128 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            uint128_field: Annotated[int, UInt128]

        test_cases = [
            0,
            1,
            2**64 - 1,  # Max UInt64
            2**64,  # Min UInt128 (high part)
            2**128 - 1,  # Max UInt128
        ]

        for value in test_cases:
            model = TestModel(uint128_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.uint128_field == value

    def test_string_type(self):
        """Test String type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            string_field: Annotated[str, String]

        test_cases = [
            "",  # Empty string
            "a",  # Single character
            "hello world",  # Regular string
            "a" * 1000,  # Long string
            "Hello, 世界!",  # Unicode string
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",  # Special characters
            "\\n\\t\\r",  # Escape characters
        ]

        for value in test_cases:
            model = TestModel(string_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.string_field == value

    def test_stringjson_type(self):
        """Test StringJson type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            json_field: Annotated[dict, StringJson]

        test_cases = [
            {},  # Empty dict
            {"key": "value"},  # Simple dict
            {"nested": {"key": "value"}},  # Nested dict
            {"list": [1, 2, 3]},  # Dict with list
            {"string": "hello", "number": 42, "boolean": True},  # Mixed types
            {"unicode": "世界", "emoji": "🌍"},  # Unicode
        ]

        for value in test_cases:
            model = TestModel(json_field=value)
            serialized = model.serialize()
            # print(value)
            deserialized = TestModel.deserialize(serialized)
            for key in value:
                assert deserialized.json_field[key] == value[key]

    def test_datetime32_type(self):
        """Test DateTime32 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            datetime_field: Annotated[datetime.datetime, DateTime32]

        test_cases = [
            datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),  # Unix epoch
            datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),  # Y2K
            datetime.datetime(
                2024, 2, 29, 12, 30, 45, tzinfo=datetime.timezone.utc
            ),  # Leap year
            datetime.datetime.now(datetime.timezone.utc),  # Current time
        ]

        for value in test_cases:
            model = TestModel(datetime_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)

    def test_datetime64_type(self):
        """Test DateTime64 type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            datetime_field: Annotated[
                datetime.datetime, DateTime64[3]
            ]  # 3 decimal places

        test_cases = [
            datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),  # Unix epoch
            datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),  # Y2K
            datetime.datetime(
                2024, 2, 29, 12, 30, 45, 123000, tzinfo=datetime.timezone.utc
            ),  # With milliseconds
            datetime.datetime.now(datetime.timezone.utc),  # Current time
        ]

        for value in test_cases:
            model = TestModel(datetime_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            # DateTime64 with 3 decimal places should preserve milliseconds
            assert abs((deserialized.datetime_field - value).total_seconds()) < 0.001

    def test_date_type(self):
        """Test Date type serialization and deserialization."""

        class TestModel(AnnotatedBaseModel):
            date_field: Annotated[datetime.date, Date]

        test_cases = [
            datetime.date(1970, 1, 1),  # Unix epoch
            datetime.date(2000, 1, 1),  # Y2K
            datetime.date(2024, 2, 29),  # Leap year
            datetime.date.today(),  # Today
            datetime.date(2038, 1, 19),  # Near 32-bit time limit
        ]

        for value in test_cases:
            model = TestModel(date_field=value)
            serialized = model.serialize()
            deserialized = TestModel.deserialize(serialized)
            assert deserialized.date_field == value

    def test_mixed_types(self):
        """Test serialization with multiple different types."""

        class TestModel(AnnotatedBaseModel):
            bool_field: Annotated[bool, Bool]
            int8_field: Annotated[int, Int8]
            uint32_field: Annotated[int, UInt32]
            float64_field: Annotated[float, Float64]
            string_field: Annotated[str, String]
            json_field: Annotated[dict, StringJson]
            date_field: Annotated[datetime.date, Date]
            datetime_field: Annotated[datetime.datetime, DateTime32]
            skipped_field: Annotated[str, Skip] = "default_value"

        model = TestModel(
            bool_field=True,
            int8_field=-100,
            uint32_field=123456789,
            float64_field=3.141592653589793,
            string_field="Hello, World!",
            json_field={"key": "value", "number": 42},
            date_field=datetime.date.today(),
            datetime_field=datetime.datetime.now(datetime.timezone.utc),
            skipped_field="This should be skipped",
        )

        serialized = model.serialize()
        deserialized = TestModel.deserialize(serialized)

        assert deserialized.bool_field == True
        assert deserialized.int8_field == -100
        assert deserialized.uint32_field == 123456789
        assert abs(deserialized.float64_field - 3.141592653589793) < 1e-15
        assert deserialized.string_field == "Hello, World!"
        assert deserialized.json_field == {"key": "value", "number": 42}
        assert deserialized.date_field == datetime.date.today()
        # Skip field should not be serialized/deserialized

    def test_edge_case_values(self):
        """Test serialization with edge case values for all types."""

        class TestModel(AnnotatedBaseModel):
            bool_field: Annotated[bool, Bool]
            int8_field: Annotated[int, Int8]
            uint8_field: Annotated[int, UInt8]
            int32_field: Annotated[int, Int32]
            uint32_field: Annotated[int, UInt32]
            int64_field: Annotated[int, Int64]
            uint64_field: Annotated[int, UInt64]
            float32_field: Annotated[float, Float32]
            float64_field: Annotated[float, Float64]
            string_field: Annotated[str, String]
            json_field: Annotated[dict, StringJson]
            date_field: Annotated[datetime.date, Date]
            datetime_field: Annotated[datetime.datetime, DateTime32]

        # Test with edge case values
        model = TestModel(
            bool_field=True,
            int8_field=-128,  # Min Int8
            uint8_field=255,  # Max UInt8
            int32_field=-2147483648,  # Min Int32
            uint32_field=4294967295,  # Max UInt32
            int64_field=-9223372036854775808,  # Min Int64
            uint64_field=18446744073709551615,  # Max UInt64
            float32_field=3.4028235e38,  # Max Float32
            float64_field=1.7976931348623157e308,  # Max Float64
            string_field="",  # Empty string
            json_field={},  # Empty dict
            date_field=datetime.date(1970, 1, 1),  # Unix epoch
            datetime_field=datetime.datetime(
                1970, 1, 1, tzinfo=datetime.timezone.utc
            ),  # Unix epoch
        )

        serialized = model.serialize()
        deserialized = TestModel.deserialize(serialized)

        assert deserialized.bool_field == True
        assert deserialized.int8_field == -128
        assert deserialized.uint8_field == 255
        assert deserialized.int32_field == -2147483648
        assert deserialized.uint32_field == 4294967295
        assert deserialized.int64_field == -9223372036854775808
        assert deserialized.uint64_field == 18446744073709551615
        assert abs(deserialized.float32_field - 3.4028235e38) < 1e32
        assert abs(deserialized.float64_field - 1.7976931348623157e308) < 1e300
        assert deserialized.string_field == ""
        assert deserialized.json_field == {}
        assert deserialized.date_field == datetime.date(1970, 1, 1)
        assert deserialized.datetime_field == datetime.datetime(
            1970, 1, 1, tzinfo=datetime.timezone.utc
        )

    def test_serialization_roundtrip_consistency(self):
        """Test that multiple serialization/deserialization cycles maintain data integrity."""

        class TestModel(AnnotatedBaseModel):
            bool_field: Annotated[bool, Bool]
            int32_field: Annotated[int, Int32]
            uint32_field: Annotated[int, UInt32]
            float64_field: Annotated[float, Float64]
            string_field: Annotated[str, String]
            json_field: Annotated[dict, StringJson]
            date_field: Annotated[datetime.date, Date]
            datetime_field: Annotated[datetime.datetime, DateTime32]

        model = TestModel(
            bool_field=True,
            int32_field=123456,
            uint32_field=987654321,
            float64_field=3.14159,
            string_field="Roundtrip Test",
            json_field={"test": "data", "number": 42},
            date_field=datetime.date.today(),
            datetime_field=datetime.datetime.now(datetime.timezone.utc),
        )

        # Perform multiple roundtrips
        current_model = model
        for _ in range(5):
            serialized = current_model.serialize()
            current_model = TestModel.deserialize(serialized)

            assert current_model.bool_field == model.bool_field
            assert current_model.int32_field == model.int32_field
            assert current_model.uint32_field == model.uint32_field
            assert abs(current_model.float64_field - model.float64_field) < 1e-15
            assert current_model.string_field == model.string_field
            assert current_model.json_field == model.json_field
            assert current_model.date_field == model.date_field
