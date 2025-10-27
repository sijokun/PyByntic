# Custom Types Guide

PyByntic makes it easy to create custom types for specialized serialization needs. This guide walks you through creating your own types.

## Understanding the Type Protocol

All PyByntic types must implement two class methods:

1. `read(cls, buf: Buffer) -> Any` - Deserializes data from a buffer
2. `write(cls, buf: Buffer, value: Any) -> None` - Serializes data to a buffer

### The Buffer API

The `Buffer` class provides the following methods:

- `read_formated(fmt: str) -> Any` - Read formatted data (uses struct format)
- `write_formated(fmt: str, value: Any) -> None` - Write formatted data
- `read_varint() -> int` - Read a variable-length integer
- `write_varint(value: int) -> None` - Write a variable-length integer
- `read_bytes(length: int) -> bytes` - Read N bytes
- `write_bytes(data: bytes) -> None` - Write bytes
- `read_fixed_str(length: int, encoding: str = "utf-8") -> str` - Read a fixed-length string
- `is_buffer_readable() -> bool` - Check if more data is available

### Struct Format Characters

Common format characters for `read_formated`/`write_formated`:

| Character | C Type              | Size | Python Type |
|-----------|---------------------|------|-------------|
| `b`       | signed char         | 1    | int         |
| `B`       | unsigned char       | 1    | int         |
| `h`       | short               | 2    | int         |
| `H`       | unsigned short      | 2    | int         |
| `i`       | int                 | 4    | int         |
| `I`       | unsigned int        | 4    | int         |
| `q`       | long long           | 8    | int         |
| `Q`       | unsigned long long  | 8    | int         |
| `f`       | float               | 4    | float       |
| `d`       | double              | 8    | float       |

---

## Simple Example: Creating a Bool Type

Here's the implementation of the built-in `Bool` type:

```python
from pybyntic.buffer import Buffer


class Bool:
    pytype = bool  # Optional: specify Python type

    @classmethod
    def read(cls, buf: Buffer) -> bool:
        return bool(buf.read_formated("b"))

    @classmethod
    def write(cls, buf: Buffer, value: bool):
        buf.write_formated("b", 1 if value else 0)
```

**Usage:**

```python
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class Config(AnnotatedBaseModel):
    enabled: Annotated[bool, Bool]


config = Config(enabled=True)
data = config.serialize()
restored = Config.deserialize(data)
```

---

## Example: IPv4 Address Type

Let's create a custom type for IPv4 addresses:

```python
from pybyntic.buffer import Buffer
import ipaddress


class IPv4:
    """Stores IPv4 addresses as 4 bytes"""

    @classmethod
    def read(cls, buf: Buffer) -> ipaddress.IPv4Address:
        data = buf.read_bytes(4)
        return ipaddress.IPv4Address(data)

    @classmethod
    def write(cls, buf: Buffer, value: ipaddress.IPv4Address):
        buf.write_bytes(value.packed)


# Usage
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class Server(AnnotatedBaseModel):
    name: Annotated[str, String]
    ip_address: Annotated[ipaddress.IPv4Address, IPv4]


server = Server(
    name="web-server",
    ip_address=ipaddress.IPv4Address("192.168.1.1")
)

data = server.serialize()
restored = Server.deserialize(data)
print(restored.ip_address)  # 192.168.1.1
```

---

## Example: UUID Type

Create a type for UUIDs:

```python
from pybyntic.buffer import Buffer
import uuid


class UUID:
    """Stores UUID as 16 bytes"""

    @classmethod
    def read(cls, buf: Buffer) -> uuid.UUID:
        data = buf.read_bytes(16)
        return uuid.UUID(bytes=data)

    @classmethod
    def write(cls, buf: Buffer, value: uuid.UUID):
        buf.write_bytes(value.bytes)


# Usage
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class Document(AnnotatedBaseModel):
    id: Annotated[uuid.UUID, UUID]
    title: Annotated[str, String]


doc = Document(
    id=uuid.uuid4(),
    title="My Document"
)

data = doc.serialize()
restored = Document.deserialize(data)
```

---

## Example: Enum Type

Create a type for Python enums:

```python
from pybyntic.buffer import Buffer
from enum import Enum


class Enum8:
    """Stores enum as 1-byte value"""

    def __init__(self, enum_class):
        self.enum_class = enum_class

    @classmethod
    def __class_getitem__(cls, enum_class):
        return cls(enum_class)

    def read(self, buf: Buffer) -> Enum:
        value = buf.read_formated("B")
        return self.enum_class(value)

    def write(self, buf: Buffer, value: Enum):
        buf.write_formated("B", value.value)


# Usage
from enum import Enum
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class Status(Enum):
    PENDING = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3


class Task(AnnotatedBaseModel):
    task_id: Annotated[int, UInt32]
    status: Annotated[Status, Enum8[Status]]


task = Task(task_id=1, status=Status.ACTIVE)
data = task.serialize()
restored = Task.deserialize(data)
print(restored.status)  # Status.ACTIVE
```

---

## Example: Variable-Length String with Maximum

Create a string type that enforces a maximum length:

```python
from pybyntic.buffer import Buffer
from typing import Any


class BoundedString:
    """Variable-length string with maximum length enforced"""

    def __init__(self, max_length: int):
        self.max_length = max_length

    @classmethod
    def __class_getitem__(cls, max_length: int):
        return cls(max_length)

    def read(self, buf: Buffer) -> str:
        length = buf.read_varint()
        if length > self.max_length:
            raise ValueError(f"String length {length} exceeds max {self.max_length}")
        data = buf.read_fixed_str(length)
        return data

    def write(self, buf: Buffer, value: str):
        data = value.encode("utf-8")
        if len(data) > self.max_length:
            raise ValueError(f"String too long (max {self.max_length} bytes)")
        buf.write_varint(len(data))
        buf.write_bytes(data)


# Usage
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, BoundedString[20]]  # Max 20 bytes


user = User(user_id=1, username="john_doe")
data = user.serialize()
restored = User.deserialize(data)
```

---

## Example: Compressed String

Create a type that stores compressed strings:

```python
import zlib
from pybyntic.buffer import Buffer


class CompressedString:
    """Stores UTF-8 string with zlib compression"""

    @classmethod
    def read(cls, buf: Buffer) -> str:
        # Read compressed data
        length = buf.read_varint()
        compressed_data = buf.read_bytes(length)
        
        # Decompress and decode
        data = zlib.decompress(compressed_data)
        return data.decode("utf-8")

    @classmethod
    def write(cls, buf: Buffer, value: str):
        # Encode and compress
        data = value.encode("utf-8")
        compressed_data = zlib.compress(data)
        
        # Write length and compressed data
        buf.write_varint(len(compressed_data))
        buf.write_bytes(compressed_data)


# Usage
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class Message(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    content: Annotated[str, CompressedString]


msg = Message(
    user_id=1,
    content="This is a very long message that will be compressed..." * 100
)

data = msg.serialize()
restored = Message.deserialize(data)
```

---

## Example: Custom Number Format

Create a type for custom number formats:

```python
from pybyntic.buffer import Buffer


class FixedPoint16:
    """
    Stores fixed-point decimal as 16-bit signed integer.
    Uses 2 decimal places (value is multiplied by 100).
    Range: -327.68 to 327.67
    """

    @classmethod
    def read(cls, buf: Buffer) -> float:
        value = buf.read_formated("h")
        return value / 100.0

    @classmethod
    def write(cls, buf: Buffer, value: float):
        # Multiply by 100 and round to nearest integer
        int_value = int(round(value * 100))
        buf.write_formated("h", int_value)


# Usage
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class Product(AnnotatedBaseModel):
    product_id: Annotated[int, UInt32]
    price: Annotated[float, FixedPoint16]  # Max price: $327.67


product = Product(product_id=1, price=19.99)
data = product.serialize()
restored = Product.deserialize(data)
print(restored.price)  # 19.99
```

---

## Advanced: Type with Parameters

Here's how to create a configurable type using `__class_getitem__`:

```python
from pybyntic.buffer import Buffer


class CustomInt:
    """Custom integer with configurable size and signedness"""

    def __init__(self, signed: bool, bits: int):
        self.signed = signed
        self.bits = bits
        
        # Map bits to format
        format_map = {
            8: "b" if signed else "B",
            16: "h" if signed else "H",
            32: "i" if signed else "I",
            64: "q" if signed else "Q"
        }
        
        if bits not in format_map:
            raise ValueError(f"Unsupported bit size: {bits}")
        
        self.format = format_map[bits]

    @classmethod
    def __class_getitem__(cls, args):
        if isinstance(args, tuple):
            signed, bits = args
        else:
            # Default to unsigned
            signed = False
            bits = args
        
        return cls(signed, bits)

    def read(self, buf: Buffer) -> int:
        return buf.read_formated(self.format)

    def write(self, buf: Buffer, value: int):
        buf.write_formated(self.format, value)


# Usage
from pybyntic import AnnotatedBaseModel
from typing import Annotated


class Data(AnnotatedBaseModel):
    # Unsigned 16-bit
    id: Annotated[int, CustomInt[16]]
    
    # Signed 32-bit (as tuple)
    offset: Annotated[int, CustomInt[True, 32]]
    
    # Unsigned 8-bit
    flags: Annotated[int, CustomInt[8]]


data = Data(id=65535, offset=-1000, flags=42)
serialized = data.serialize()
restored = Data.deserialize(serialized)
```

---

## Advanced: Type with Initialization

Some types need initialization parameters:

```python
from pybyntic.buffer import Buffer
from typing import Any, Callable


class TransformType:
    """
    Applies a transformation during serialization/deserialization.
    """

    def __init__(self, inner_type, transform_to_bytes: Callable, transform_from_bytes: Callable):
        self.inner_type = inner_type
        self.transform_to_bytes = transform_to_bytes
        self.transform_from_bytes = transform_from_bytes

    @classmethod
    def __class_getitem__(cls, args):
        inner_type, transform_to, transform_from = args
        return cls(inner_type, transform_to, transform_from)

    def read(self, buf: Buffer) -> Any:
        # Read as string
        data = self.inner_type.read(buf)
        
        # Apply transformation
        return self.transform_from_bytes(data)

    def write(self, buf: Buffer, value: Any):
        # Apply transformation
        data = self.transform_to_bytes(value)
        
        # Write as string
        self.inner_type.write(buf, data)


# Usage with base64 encoding
import base64

Base64String = TransformType[
    String,
    lambda x: base64.b64encode(x.encode()).decode(),
    lambda x: base64.b64decode(x).decode()
]

class Config(AnnotatedBaseModel):
    secret: Annotated[str, Base64String]


config = Config(secret="sensitive data")
data = config.serialize()
restored = Config.deserialize(data)
```

---

## Testing Custom Types

Create tests for your custom types:

```python
import pytest
from pybyntic import AnnotatedBaseModel
from pybyntic.types import UInt32
from typing import Annotated
from pybyntic.buffer import Buffer


class MyCustomType:
    @classmethod
    def read(cls, buf: Buffer):
        return buf.read_formated("i")

    @classmethod
    def write(cls, buf: Buffer, value: int):
        buf.write_formated("i", value)


class TestModel(AnnotatedBaseModel):
    id: Annotated[int, UInt32]
    value: Annotated[int, MyCustomType]


def test_my_custom_type():
    model = TestModel(id=1, value=42)
    data = model.serialize()
    restored = TestModel.deserialize(data)
    assert restored.value == 42
```

---

## Next Steps

- [Main Documentation](index.md)
- [Types Reference](types.md)
- [Usage Examples](usage-examples.md)

