# PyByntic Types Reference

This document provides a comprehensive reference for all types available in PyByntic.

## Overview

PyByntic provides a rich set of types for binary serialization. Each type specifies how data is encoded into bytes and decoded back into Python objects.

## Type Categories

### Skip Fields

#### `Skip`

Skips a field during serialization and deserialization. Useful for fields that shouldn't be persisted.

```python
from pybyntic.types import Skip

class Config(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    temp_field: Annotated[str, Skip]
```

---

## Boolean Type

#### `Bool`

Serializes boolean values as a single byte (1 for True, 0 for False).

```python
from pybyntic.types import Bool

class User(AnnotatedBaseModel):
    is_active: Annotated[bool, Bool]
```

**Format:** `b` (1 byte)  
**Python Type:** `bool`

---

## Signed Integer Types

### `Int8`

8-bit signed integer (-128 to 127).

```python
from pybyntic.types import Int8

class Data(AnnotatedBaseModel):
    temperature: Annotated[int, Int8]
```

**Format:** `b` (1 byte)  
**Python Type:** `int`  
**Range:** -128 to 127

### `Int16`

16-bit signed integer (-32,768 to 32,767).

```python
from pybyntic.types import Int16

class Data(AnnotatedBaseModel):
    year: Annotated[int, Int16]
```

**Format:** `h` (2 bytes)  
**Python Type:** `int`  
**Range:** -32,768 to 32,767

### `Int32`

32-bit signed integer (-2,147,483,648 to 2,147,483,647).

```python
from pybyntic.types import Int32

class Data(AnnotatedBaseModel):
    timestamp: Annotated[int, Int32]
```

**Format:** `i` (4 bytes)  
**Python Type:** `int`  
**Range:** -2,147,483,648 to 2,147,483,647

### `Int64`

64-bit signed integer.

```python
from pybyntic.types import Int64

class Data(AnnotatedBaseModel):
    big_number: Annotated[int, Int64]
```

**Format:** `q` (8 bytes)  
**Python Type:** `int`  
**Range:** -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807

---

## Unsigned Integer Types

### `UInt8`

8-bit unsigned integer (0 to 255).

```python
from pybyntic.types import UInt8

class Data(AnnotatedBaseModel):
    version: Annotated[int, UInt8]
```

**Format:** `B` (1 byte)  
**Python Type:** `int`  
**Range:** 0 to 255

### `UInt16`

16-bit unsigned integer (0 to 65,535).

```python
from pybyntic.types import UInt16

class Data(AnnotatedBaseModel):
    port: Annotated[int, UInt16]
```

**Format:** `H` (2 bytes)  
**Python Type:** `int`  
**Range:** 0 to 65,535

### `UInt32`

32-bit unsigned integer (0 to 4,294,967,295).

```python
from pybyntic.types import UInt32

class Data(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
```

**Format:** `I` (4 bytes)  
**Python Type:** `int`  
**Range:** 0 to 4,294,967,295

### `UInt64`

64-bit unsigned integer.

```python
from pybyntic.types import UInt64

class Data(AnnotatedBaseModel):
    large_id: Annotated[int, UInt64]
```

**Format:** `Q` (8 bytes)  
**Python Type:** `int`  
**Range:** 0 to 18,446,744,073,709,551,615

### `UInt128`

128-bit unsigned integer. Stored as two 64-bit values (high and low).

```python
from pybyntic.types import UInt128

class Data(AnnotatedBaseModel):
    huge_number: Annotated[int, UInt128]
```

**Format:** Two `Q` (16 bytes total)  
**Python Type:** `int`

---

## Floating Point Types

### `Float32`

Single-precision floating point (IEEE 754).

```python
from pybyntic.types import Float32

class Data(AnnotatedBaseModel):
    temperature: Annotated[float, Float32]
```

**Format:** `f` (4 bytes)  
**Python Type:** `float`  
**Precision:** ~7 decimal digits

### `Float64`

Double-precision floating point (IEEE 754).

```python
from pybyntic.types import Float64

class Data(AnnotatedBaseModel):
    precise_value: Annotated[float, Float64]
```

**Format:** `d` (8 bytes)  
**Python Type:** `float`  
**Precision:** ~15 decimal digits

---

## String Types

### `String`

Variable-length UTF-8 string with varint length prefix.

```python
from pybyntic.types import String

class User(AnnotatedBaseModel):
    username: Annotated[str, String]
```

**Format:** Varint length + UTF-8 bytes  
**Python Type:** `str`  
**Encoding:** UTF-8

**Example:**
- The string "hello" is encoded as: `length_varint` + `b"hello"`
- Short strings use 1 byte for length, longer strings use more

### `FixedString[n]`

Fixed-length string of n bytes.

```python
from pybyntic.types import FixedString

class User(AnnotatedBaseModel):
    # Fixed 2-byte string
    language: Annotated[str, FixedString[2]]
    
    # Fixed 4-byte string with custom encoding
    country: Annotated[str, FixedString[4, "UTF-16LE"]]
```

**Parameters:**
- `length` (int): Number of bytes (not characters)
- `encoding` (str, optional): Character encoding (default: "utf-8")

**Behavior:**
- If string is shorter than `length`: padded with null bytes
- If string is longer than `length`: truncated

**Best Practices:**
- Use fixed-byte encodings (e.g., "UTF-16LE" or "ASCII") when possible
- Useful for codes (language, country, currency)
- Good for predefined formats (IDs, codes, etc.)

**Example:**
```python
# Language code: "en" → 2 bytes
language: Annotated[str, FixedString[2]] = "en"

# Country code: "US" in UTF-16LE → 4 bytes
country: Annotated[str, FixedString[4, "UTF-16LE"]] = "US"
```

### `StringJson`

Variable-length JSON string, deserialized as a dictionary.

```python
from pybyntic.types import StringJson

class Config(AnnotatedBaseModel):
    metadata: Annotated[dict, StringJson]
```

**Format:** Varint length + JSON bytes  
**Python Type:** `dict`  
**Note:** Stored as UTF-8 JSON, decoded via `json.loads`

---

## Date and Time Types

### `Date`

Date stored as days since `1970-01-01`.

```python
from pybyntic.types import Date
import datetime

class User(AnnotatedBaseModel):
    join_date: Annotated[datetime.date, Date]
```

**Format:** `H` (2 bytes - days since epoch)  
**Python Type:** `datetime.date`  
**Epoch:** 1970-01-01  
**Range:** Up to ~82 years from epoch

### `DateTime32`

Timestamp stored as seconds since Unix epoch.

```python
from pybyntic.types import DateTime32
import datetime

class Event(AnnotatedBaseModel):
    created_at: Annotated[datetime.datetime, DateTime32]
```

**Format:** `I` (4 bytes - seconds since epoch)  
**Python Type:** `datetime.datetime` (UTC)  
**Epoch:** 1970-01-01 00:00:00 UTC  
**Range:** Up to 2038 (Year 2038 problem)

### `DateTime64[precision]`

High-precision timestamp with configurable precision.

```python
from pybyntic.types import DateTime64
import datetime

class Event(AnnotatedBaseModel):
    # Millisecond precision (default)
    created_at: Annotated[datetime.datetime, DateTime64]
    
    # Microsecond precision
    precise_time: Annotated[datetime.datetime, DateTime64[6]]
```

**Parameters:**
- `precision` (int): Decimal places (default: 3 for milliseconds)

**Format:** `Q` (8 bytes)  
**Python Type:** `datetime.datetime` (UTC)  
**Default Precision:** 3 (milliseconds)  
**Storage:** `timestamp × 10^precision` converted to int

**Examples:**
```python
# Millisecond precision (default)
created_at: Annotated[datetime.datetime, DateTime64]

# Microsecond precision
precise: Annotated[datetime.datetime, DateTime64[6]]

# Nanosecond precision
ultra_precise: Annotated[datetime.datetime, DateTime64[9]]
```

---

## Special Types

### `Nullable[T]`

Wraps a type to make it nullable. Adds a boolean flag before the value.

```python
from pybyntic.types import Nullable
from typing import Optional

class User(AnnotatedBaseModel):
    user_id: Annotated[int, UInt32]
    username: Annotated[Optional[str], Nullable[String]]
```

**Format:** 1 byte flag (`1` if null, `0` if not) + inner type  
**Python Type:** `Optional[T]` where T is the inner type

**Note:** Adding a null flag increases serialized size by 1 byte. Consider using default values instead if you want to reduce size.

---

## Type Selection Guide

### For IDs and Counts

- Small IDs (< 65,536): `UInt16`
- Standard IDs (most cases): `UInt32`
- Large IDs (> 4 billion): `UInt64`
- Very large IDs: `UInt128`

### For Dates and Times

- Dates: `Date` (2 bytes, ~82 year range)
- Timestamps (second precision): `DateTime32` (4 bytes)
- Precise timestamps: `DateTime64` or `DateTime64[6]` (8 bytes)

### For Text

- Variable text: `String` (varint length prefix)
- Fixed codes: `FixedString[n]` (known length)
- JSON data: `StringJson` (for dictionaries)

### For Numeric Values

- Small integers: `Int8` or `Int16`
- Standard integers: `Int32` or `UInt32`
- Large integers: `Int64` or `UInt64`
- Floats: `Float32` (4 bytes) or `Float64` (8 bytes)

---

## Complete Type Table

| Type Name        | Format / Encoding | Bytes | Python Type      | Notes                                      |
|------------------|-------------------|-------|------------------|--------------------------------------------|
| `Skip`           | — (no-op)         | 0     | `None`           | Skips field                                 |
| `Bool`           | `b`               | 1     | `bool`           | Writes `1` or `0`                          |
| `Int8`           | `b`               | 1     | `int`            | Signed 8-bit (-128 to 127)                 |
| `Int16`          | `h`               | 2     | `int`            | Signed 16-bit                              |
| `Int32`          | `i`               | 4     | `int`            | Signed 32-bit                              |
| `Int64`          | `q`               | 8     | `int`            | Signed 64-bit                              |
| `UInt8`          | `B`               | 1     | `int`            | Unsigned 8-bit (0 to 255)                  |
| `UInt16`         | `H`               | 2     | `int`            | Unsigned 16-bit (0 to 65,535)              |
| `UInt32`         | `I`               | 4     | `int`            | Unsigned 32-bit (0 to 4.2 billion)         |
| `UInt64`         | `Q`               | 8     | `int`            | Unsigned 64-bit                            |
| `UInt128`        | 2× `Q` (hi/lo)    | 16    | `int`            | 128-bit unsigned, stored as 2×64-bit       |
| `Float32`        | `f`               | 4     | `float`          | IEEE754 single precision                   |
| `Float64`        | `d`               | 8     | `float`          | IEEE754 double precision                   |
| `String`         | varint + bytes    | var   | `str`            | UTF-8 string, with varint length prefix   |
| `FixedString[n]` | `bytes`           | n     | `str`            | Fixed-length string of N bytes            |
| `StringJson`     | varint + bytes    | var   | `dict`           | UTF-8 JSON, decoded via `json.loads`      |
| `DateTime32`     | `I`               | 4     | `datetime` (UTC) | Seconds since epoch                        |
| `DateTime64[p]`  | `Q`               | 8     | `datetime` (UTC) | Timestamp in `10^-p` seconds precision     |
| `Date`           | `H`               | 2     | `date`           | Days since `1970-01-01`                    |

---

## Next Steps

- [Main Documentation](index.md)
- [Usage Examples](usage-examples.md)
- [Custom Types Guide](custom-types.md)

