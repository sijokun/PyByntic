# PyByntic Usage Examples

This document provides comprehensive examples demonstrating how to use PyByntic for various scenarios.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Lists](#lists)
3. [Nested Models](#nested-models)
4. [Nullable Fields](#nullable-fields)
5. [Fixed-Length Strings](#fixed-length-strings)
6. [Compression](#compression)
7. [Advanced Patterns](#advanced-patterns)

---

## Basic Usage

### Simple Model

The most basic PyByntic model consists of fields annotated with PyByntic types.

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String, Bool, Date
from typing import Annotated
import datetime


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]


# Create a user
user = User(
    user_id=123,
    username="admin",
    is_active=True,
    join_date=datetime.date.today()
)

# Serialize to bytes
serialized = user.serialize()
print(f"Serialized size: {len(serialized)} bytes")

# Deserialize from bytes
deserialized = User.deserialize(serialized)
print(deserialized)  # User(user_id=123, username='admin', ...)
```

---

## Lists

PyByntic supports lists of primitive types. Use `list[Type]` annotation where `Type` is a PyByntic type.

### List of Primitives

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String
from typing import Annotated


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    roles: Annotated[list[str], list[String]]


# Create user with roles
user = User(
    user_id=123,
    username="admin",
    roles=["admin", "editor", "user", "viewer"]
)

# Serialize and deserialize
data = user.serialize()
restored = User.deserialize(data)

print(restored.roles)  # ['admin', 'editor', 'user', 'viewer']
```

### List of Numbers

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt16
from typing import Annotated


class SensorData(AnnotatedBaseModel):
    sensor_id: Annotated[int, UInt16]
    readings: Annotated[list[int], list[UInt16]]


# Create sensor data
data = SensorData(
    sensor_id=1,
    readings=[42, 43, 44, 45, 100]
)

# Serialize and deserialize
serialized = data.serialize()
restored = SensorData.deserialize(serialized)

print(restored.readings)  # [42, 43, 44, 45, 100]
```

---

## Nested Models

PyByntic supports nested models by referencing other `AnnotatedBaseModel` classes.

### Single Nested Model

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import String, UInt8, UInt32
from typing import Annotated


class Role(AnnotatedBaseModel):
    role_id: Annotated[int, UInt8]
    role_name: Annotated[str, String]


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    role: Role


# Create nested structure
user = User(
    user_id=123,
    username="admin",
    role=Role(role_id=1, role_name="Administrator")
)

# Serialize and deserialize
serialized = user.serialize()
restored = User.deserialize(serialized)

print(restored.role.role_name)  # "Administrator"
```

### Multiple Nested Models

```python
class Address(AnnotatedBaseModel):
    street: Annotated[str, String]
    city: Annotated[str, String]
    postal_code: Annotated[int, UInt32]


class Contact(AnnotatedBaseModel):
    email: Annotated[str, String]
    phone: Annotated[str, String]


class Person(AnnotatedBaseModel):
    person_id: Annotated[int, UInt32]
    name: Annotated[str, String]
    address: Address
    contact: Contact


# Create complex nested structure
person = Person(
    person_id=1,
    name="John Doe",
    address=Address(
        street="123 Main St",
        city="Springfield",
        postal_code=12345
    ),
    contact=Contact(
        email="john@example.com",
        phone="555-0100"
    )
)

# Serialize and deserialize
serialized = person.serialize()
restored = Person.deserialize(serialized)
```

---

## Nullable Fields

Use `Nullable` to handle optional fields. This adds a 1-byte flag to indicate null values.

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import Nullable, String, UInt32
from typing import Annotated, Optional


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[Optional[str], Nullable[String]]


# Example with value
user_with_name = User(user_id=123, username="admin")
data = user_with_name.serialize()
restored = User.deserialize(data)
print(restored.username)  # "admin"

# Example with null
user_without_name = User(user_id=456, username=None)
data = user_without_name.serialize()
restored = User.deserialize(data)
print(restored.username)  # None
```

**Note:** `Nullable` adds 1 byte overhead. For better size efficiency, consider using default values instead:

```python
class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String] = ""  # Empty string default instead of None
```

---

## Fixed-Length Strings

Use `FixedString` when you know the exact byte length of a string field.

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import FixedString, String, UInt32
from typing import Annotated


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    
    # Language code: 2 bytes
    language: Annotated[str, FixedString[2]]
    
    # Currency code: 3 bytes
    currency: Annotated[str, FixedString[3]]


# Create user
user = User(
    user_id=123,
    username="admin",
    language="en",  # Will be padded to 2 bytes
    currency="USD"  # Will be padded to 3 bytes
)

# Serialize
serialized = user.serialize()
restored = User.deserialize(serialized)

print(restored.language)  # "en"
print(restored.currency)  # "USD"
```

### Custom Encoding

Use custom encodings for fixed-length strings:

```python
class Config(AnnotatedBaseModel):
    # UTF-16LE encoding: 2 bytes per character
    language: Annotated[str, FixedString[4, "UTF-16LE"]]
    
    # UTF-32BE encoding: 4 bytes per character
    region: Annotated[str, FixedString[8, "UTF-32BE"]]


config = Config(
    language="en",  # 2 chars × 2 bytes = 4 bytes
    region="us"     # 2 chars × 4 bytes = 8 bytes
)

serialized = config.serialize()
restored = Config.deserialize(serialized)
```

---

## Compression

PyByntic supports custom encoders and decoders. Use compression to further reduce size for large datasets.

```python
import zlib
from pybyntic import AnnotatedBaseModel
from pybyntic.types import Bool, Date, String, UInt32
from typing import Annotated
import datetime


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]


# Create user
user = User(
    user_id=123,
    username="admin",
    is_active=True,
    join_date=datetime.date.today()
)

# Serialize with compression
serialized = user.serialize(encoder=zlib.compress)
print(f"Compressed size: {len(serialized)} bytes")

# Deserialize with decompression
deserialized = User.deserialize(serialized, decoder=zlib.decompress)
print(deserialized)
```

### Custom Encoder/Decoder

```python
import base64


def my_encoder(data: bytes) -> bytes:
    # Add your custom encoding logic
    return base64.b64encode(zlib.compress(data))


def my_decoder(data: bytes) -> bytes:
    # Add your custom decoding logic
    return zlib.decompress(base64.b64decode(data))


# Use custom encoder/decoder
serialized = user.serialize(encoder=my_encoder)
deserialized = User.deserialize(serialized, decoder=my_decoder)
```

---

## Advanced Patterns

### Lists of Nested Models

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32, String, UInt8
from typing import Annotated


class Permission(AnnotatedBaseModel):
    permission_id: Annotated[int, UInt8]
    permission_name: Annotated[str, String]


class Role(AnnotatedBaseModel):
    role_id: Annotated[int, UInt8]
    role_name: Annotated[str, String]
    permissions: Annotated[list[Permission], list]


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    roles: Annotated[list[Role], list]


# Create complex structure
user = User(
    user_id=1,
    username="admin",
    roles=[
        Role(
            role_id=1,
            role_name="Administrator",
            permissions=[
                Permission(permission_id=1, permission_name="read"),
                Permission(permission_id=2, permission_name="write"),
                Permission(permission_id=3, permission_name="delete")
            ]
        ),
        Role(
            role_id=2,
            role_name="Editor",
            permissions=[
                Permission(permission_id=1, permission_name="read"),
                Permission(permission_id=2, permission_name="write")
            ]
        )
    ]
)

# Serialize and deserialize
serialized = user.serialize()
restored = User.deserialize(serialized)

print(f"User has {len(restored.roles)} roles")
for role in restored.roles:
    print(f"{role.role_name}: {len(role.permissions)} permissions")
```

### JSON Fields

Use `StringJson` to store complex nested data as JSON:

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import StringJson, UInt32
from typing import Annotated


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    metadata: Annotated[dict, StringJson]


# Create user with complex metadata
user = User(
    user_id=123,
    metadata={
        "preferences": {
            "theme": "dark",
            "language": "en"
        },
        "tags": ["vip", "active", "premium"],
        "settings": {
            "notifications": True,
            "auto_save": False
        }
    }
)

# Serialize and deserialize
serialized = user.serialize()
restored = User.deserialize(serialized)

print(restored.metadata["preferences"]["theme"])  # "dark"
```

### High-Precision Timestamps

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import DateTime64, UInt32
from typing import Annotated
import datetime


class Event(AnnotatedBaseModel):
    event_id: Annotated[int, UInt32]
    
    # Millisecond precision (default)
    created_at: Annotated[datetime.datetime, DateTime64]
    
    # Microsecond precision
    processed_at: Annotated[datetime.datetime, DateTime64[6]]


# Create event with precise timestamps
event = Event(
    event_id=1,
    created_at=datetime.datetime.now(tz=datetime.timezone.utc),
    processed_at=datetime.datetime.now(tz=datetime.timezone.utc)
)

# Serialize and deserialize
serialized = event.serialize()
restored = Event.deserialize(serialized)
```

### Timezone-Aware Timestamps

Use `DateTime32TZ` or `DateTime64TZ` to store timestamps with timezone information:

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import DateTime32TZ, DateTime64TZ, UInt32
from typing import Annotated
import datetime
import zoneinfo


class Event(AnnotatedBaseModel):
    event_id: Annotated[int, UInt32]
    
    # Second precision with timezone
    created_at: Annotated[datetime.datetime, DateTime32TZ]
    
    # Millisecond precision with timezone
    processed_at: Annotated[datetime.datetime, DateTime64TZ[3]]


# Create event with timezone-aware timestamps
event = Event(
    event_id=1,
    created_at=datetime.datetime.now().astimezone(zoneinfo.ZoneInfo("America/New_York")),
    processed_at=datetime.datetime.now().astimezone(zoneinfo.ZoneInfo("Asia/Tokyo"))
)

# Serialize and deserialize
serialized = event.serialize()
restored = Event.deserialize(serialized)

# Note: The timezone offset is preserved, but the timezone name may differ
# The offset will be correct, but it may be represented as a fixed offset
# instead of the original named timezone (e.g., "America/New_York")
```

**Important:** Timezone-aware types store the UTC offset in minutes, not the timezone name. This means:
- The correct UTC offset is preserved
- The exact timezone name (like "America/New_York") is not preserved
- If you need to preserve the timezone name, store UTC time and the timezone separately

### Large Numbers

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt128, String
from typing import Annotated


class Transaction(AnnotatedBaseModel):
    transaction_id: Annotated[int, UInt128]  # Supports huge numbers
    description: Annotated[str, String]


# Create transaction with very large ID
transaction = Transaction(
    transaction_id=123456789012345678901234567890123456789,
    description="Purchase"
)

# Serialize and deserialize
serialized = transaction.serialize()
restored = Transaction.deserialize(serialized)
```

---

## Complete Example: User Management System

Here's a comprehensive example combining multiple features:

```python
from pybyntic import AnnotatedBaseModel
from pybyntic.types import (
    Bool, Date, DateTime64, FixedString, String, UInt32, UInt8
)
from typing import Annotated, Optional
import datetime


class Address(AnnotatedBaseModel):
    street: Annotated[str, String]
    city: Annotated[str, String]
    postal_code: Annotated[int, UInt32]


class Contact(AnnotatedBaseModel):
    email: Annotated[str, String]
    phone: Annotated[Optional[str], Optional[String]]


class Role(AnnotatedBaseModel):
    role_id: Annotated[int, UInt8]
    role_name: Annotated[str, String]
    permissions: Annotated[list[str], list[String]]


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    is_active: Annotated[bool, Bool]
    join_date: Annotated[datetime.date, Date]
    last_login: Annotated[datetime.datetime, DateTime64]
    language: Annotated[str, FixedString[2]]
    currency: Annotated[str, FixedString[3]]
    address: Address
    contact: Contact
    roles: Annotated[list[Role], list]


# Create a complete user
user = User(
    user_id=12345,
    username="john_doe",
    is_active=True,
    join_date=datetime.date(2023, 1, 1),
    last_login=datetime.datetime.now(tz=datetime.timezone.utc),
    language="en",
    currency="USD",
    address=Address(
        street="123 Main St",
        city="Springfield",
        postal_code=12345
    ),
    contact=Contact(
        email="john@example.com",
        phone="555-1234"
    ),
    roles=[
        Role(
            role_id=1,
            role_name="Administrator",
            permissions=["read", "write", "delete", "manage_users"]
        ),
        Role(
            role_id=2,
            role_name="Editor",
            permissions=["read", "write"]
        )
    ]
)

# Serialize
serialized = user.serialize()
print(f"Serialized size: {len(serialized)} bytes")

# With compression
compressed = user.serialize(encoder=zlib.compress)
print(f"Compressed size: {len(compressed)} bytes")

# Deserialize
restored = User.deserialize(compressed, decoder=zlib.decompress)
print(restored)
```

---

## Next Steps

- [Main Documentation](index.md)
- [Types Reference](types.md)
- [Custom Types Guide](custom-types.md)

