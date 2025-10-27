# PyByntic Documentation

![Tests](https://github.com/sijokun/PyByntic/workflows/Tests/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/sijokun/PyByntic/badge.svg?branch=master)](https://coveralls.io/github/sijokun/PyByntic?branch=master)
[![PyPI version](https://badge.fury.io/py/PyByntic.svg)](https://badge.fury.io/py/PyByntic)
[![Downloads](https://static.pepy.tech/personalized-badge/PyByntic?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/PyByntic)

PyByntic extends Pydantic with binary-typed fields and automatic byte-level serialization. Define models using familiar Pydantic syntax and turn them into compact binary payloads with full control over layout and numeric precision.

## Overview

PyByntic provides a powerful solution for efficient binary serialization of Python models. It offers:

- **Binary Serialization**: Convert Pydantic models to compact binary format
- **Type Safety**: Full type annotations with custom binary types
- **Nested Models**: Support for nested models and lists
- **Custom Encoders**: Support for compression and custom encoding
- **Size Efficiency**: Significantly smaller than JSON serialization

## Quick Start

### Installation

```bash
pip install pybyntic
```

### Basic Example

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


# Create and serialize
user = User(
    user_id=123,
    username='admin',
    is_active=True,
    join_date=datetime.date.today()
)

# Serialize to bytes
serialized = user.serialize()

# Deserialize from bytes
deserialized = User.deserialize(serialized)
```

## Benchmark

PyByntic achieves exceptional memory efficiency. Based on 2 million user records containing various types (UInt16, UInt32, Int32, Int64, Bool, Float32, String, DateTime32) with nested objects (roles and permissions), PyByntic provides the smallest memory usage of all tested solutions.

<img width="1580" height="980" alt="benchmark" src="https://github.com/user-attachments/assets/7ebff40b-4d53-4195-b674-b9caf0fa2cf0" />

## Key Concepts

### AnnotatedBaseModel

`AnnotatedBaseModel` is the base class for all PyByntic models. It extends Pydantic's `BaseModel` with binary serialization capabilities.

```python
from pybyntic import AnnotatedBaseModel

class MyModel(AnnotatedBaseModel):
    # Define fields with annotations
    pass
```

### Type Annotations

Fields are annotated using Python's `Annotated` type hint with a PyByntic type:

```python
from typing import Annotated
from pybyntic.types import UInt32, String

class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
```

### Serialization Methods

**Serialize to bytes:**

```python
data = user.serialize()
```

**Deserialize from bytes:**

```python
user = User.deserialize(data)
```

**With compression:**

```python
import zlib

# Serialize with compression
data = user.serialize(encoder=zlib.compress)

# Deserialize with decompression
user = User.deserialize(data, decoder=zlib.decompress)
```

## Documentation Structure

- [**Types**](types.md) - Complete reference for all available types
- [**Usage Examples**](usage-examples.md) - Comprehensive examples of PyByntic features
- [**Custom Types**](custom-types.md) - Guide to implementing custom types

## Advanced Features

### Lists

PyByntic supports lists of primitive types and nested models:

```python
class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    roles: Annotated[list[str], list[String]]
```

### Nested Models

Define models within models:

```python
class Role(AnnotatedBaseModel):
    role_id: Annotated[int, UInt8]
    role_name: Annotated[str, String]

class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[str, String]
    role: Role
```

### Nullable Fields

Handle optional values with the `Nullable` type:

```python
from pybyntic.types import Nullable

class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[Optional[str], Nullable[String]]
```

### Fixed-Length Strings

Use `FixedString` for strings with known lengths:

```python
from pybyntic.types import FixedString

class User(AnnotatedBaseModel):
    language: Annotated[str, FixedString[2]]  # 2 bytes
    country: Annotated[str, FixedString[4, "UTF-16LE"]]  # 4 bytes with custom encoding
```

## Testing

Run the test suite:

```bash
poetry run pytest
```

## Development

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poe test

# Format code
poe autoformat
```

## See Also

- [Types Reference](types.md)
- [Usage Examples](usage-examples.md)
- [Custom Types Guide](custom-types.md)

