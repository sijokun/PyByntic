# PyByntic

![Tests](https://github.com/sijokun/PyByntic/workflows/Tests/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/sijokun/PyByntic/badge.svg?branch=master)](https://coveralls.io/github/sijokun/PyByntic?branch=master)
[![PyPI version](https://badge.fury.io/py/PyByntic.svg)](https://badge.fury.io/py/PyByntic)
[![Downloads](https://static.pepy.tech/personalized-badge/PyByntic?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/PyByntic)


PyByntic extends Pydantic with binary-typed fields and automatic byte-level serialization. Define models using familiar Pydantic syntax and turn them into compact binary payloads with full control over layout and numeric precision.

## Features

- **Binary Serialization**: Convert Pydantic models to compact binary format
- **Type Safety**: Full type annotations with custom binary types
- **Nested Models**: Support for nested models and lists
- **Custom Encoders**: Support for compression and custom encoding
- **Size Efficiency**: Significantly smaller than JSON serialization

## Installation

```bash
pip install pybyntic
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

## Usage

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

## Examples

See the `examples/` directory for more comprehensive examples including:
- Basic serialization
- List handling
- Nested models
- Compression
- Benchmarking

## Types

| Type Name       | Format / Encoding | Python Type Returned | Notes                                                |
| --------------- |-------------------|----------------------|------------------------------------------------------|
| `Skip`          | — (no-op)         | `None`               | Skips field                                          |
| `Bool`          | `b` (1 byte)      | `bool`               | Writes `1` or `0`                                    |
| `Int8`          | `b`               | `int`                | Signed 8-bit integer                                 |
| `Int16`         | `h`               | `int`                | Signed 16-bit integer                                |
| `Int32`         | `i`               | `int`                | Signed 32-bit integer                                |
| `Int64`         | `q`               | `int`                | Signed 64-bit integer                                |
| `UInt8`         | `B`               | `int`                | Unsigned 8-bit integer                               |
| `UInt16`        | `H`               | `int`                | Unsigned 16-bit integer                              |
| `UInt32`        | `I`               | `int`                | Unsigned 32-bit integer                              |
| `UInt64`        | `Q`               | `int`                | Unsigned 64-bit integer                              |
| `UInt128`       | 2× `Q` (hi/lo)    | `int`                | 128-bit unsigned integer, stored as 2×64-bit         |
| `Float32`       | `f`               | `float`              | IEEE754 single precision                             |
| `Float64`       | `d`               | `float`              | IEEE754 double precision                             |
| `String`        | `varint + bytes`  | `str`                | UTF-8 string, with varint length prefix              |
| `StringJson`    | `varint + bytes`  | `dict`               | UTF-8 JSON, decoded via `json.loads`                 |
| `DateTime32`    | `I`               | `datetime` (UTC)     | Seconds since epoch                                  |
| `DateTime64[p]` | `Q`               | `datetime` (UTC)     | Timestamp in `10^-p` seconds precision (default p=3) |
| `Date`          | `H`               | `date`               | Days since `1970-01-01`                              |


## Implementing Custom Types
Example of a type implementation:

```python
from pybyntic.buffer import Buffer


class Bool:
	@classmethod
	def read(cls, buf: Buffer):
		return bool(buf.read_formated("b"))

	@classmethod
	def write(cls, buf: Buffer, value):
		buf.write_formated("b", 1 if value else 0)
```

Type classes must implement `read` and `write` class methods to handle serialization and deserialization.
Read methods receive a `Buffer` instance for byte operations, and write methods receive a `Buffer` and the value to serialize.

## Testing

The project includes comprehensive tests covering:
- Basic serialization/deserialization
- List handling
- Nested models and lists
- Dictionary serialization with JSON
- Compression functionality
- Individual type testing

Run tests with:
```bash
poetry run pytest
```

