import json
from datetime import date, datetime, timedelta, timezone
from typing import Any, Generic, Protocol, Type, TypeVar

from pybyntic.buffer import Buffer

ZERO_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)


class TypeProto(Protocol):
    @classmethod
    def read(cls, buf: Buffer) -> Any:
        ...

    @classmethod
    def write(cls, buf: Buffer, value: Any) -> None:
        ...


class Skip:
    @classmethod
    def read(cls, _: Buffer) -> None:
        return None

    @classmethod
    def write(cls, buf: Buffer, value: Any):
        pass


class Bool:
    @classmethod
    def read(cls, buf: Buffer) -> bool:
        return bool(buf.read_formated("b"))

    @classmethod
    def write(cls, buf: Buffer, value: bool):
        buf.write_formated("b", 1 if value else 0)


class FmtType:
    fmt: str = "b"

    @classmethod
    def read(cls, buf: Buffer) -> int | float:
        return buf.read_formated(cls.fmt)

    @classmethod
    def write(cls, buf: Buffer, value: int | float):
        buf.write_formated(cls.fmt, value)


class Int8(FmtType):
    fmt = "b"


class Int16(FmtType):
    fmt = "h"


class Int32(FmtType):
    fmt = "i"


class Int64(FmtType):
    fmt = "q"


class UInt8(FmtType):
    fmt = "B"


class UInt16(FmtType):
    fmt = "H"


class UInt32(FmtType):
    fmt = "I"


class UInt64(FmtType):
    fmt = "Q"


class Float32(FmtType):
    fmt = "f"


class Float64(FmtType):
    fmt = "d"


class UInt128:
    @classmethod
    def read(cls, buf: Buffer) -> int:
        hi = buf.read_formated("Q")
        lo = buf.read_formated("Q")
        return (hi << 64) + lo

    @classmethod
    def write(cls, buf: Buffer, value):
        hi = value >> 64
        lo = value & 0xFFFFFFFFFFFFFFFF
        buf.write_formated("Q", hi)
        buf.write_formated("Q", lo)


class String:
    @classmethod
    def read(cls, buf: Buffer) -> str | bytes:
        length = buf.read_varint()
        data = buf.read_fixed_str(length)
        return data

    @classmethod
    def write(cls, buf: Buffer, value):
        data = value.encode("utf-8")
        buf.write_varint(len(data))
        buf.write_bytes(data)


class StringJson:
    @classmethod
    def read(cls, buf: Buffer) -> dict[str, Any]:
        length = buf.read_varint()
        data = buf.read_fixed_str(length)
        return json.loads(data if data else "{}")

    @classmethod
    def write(cls, buf: Buffer, value):
        value = json.dumps(value).encode()
        buf.write_varint(len(value))
        buf.write_bytes(value)


class DateTime32:
    @classmethod
    def read(cls, buf: Buffer) -> datetime:
        if not buf.is_buffer_readable():
            return ZERO_UTC

        return datetime.fromtimestamp(buf.read_formated("I"), tz=timezone.utc)

    @classmethod
    def write(cls, buf: Buffer, value: datetime):
        UInt32.write(buf, int(value.timestamp()))


class DateTime64:
    precision = 3

    def __init__(self, precision):
        self.precision = precision

    @classmethod
    def __class_getitem__(cls, precision=3):
        return cls(precision)

    def read(self, buf: Buffer) -> datetime:
        ticks = buf.read_formated("Q")

        divisor = 10**self.precision

        timestamp = ticks / divisor

        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def write(self, buf: Buffer, value):
        divisor = 10**self.precision
        ticks = int(value.timestamp() * divisor)
        buf.write_formated("Q", ticks)


class Date:
    @classmethod
    def read(cls, buf: Buffer) -> date:
        return date(1970, 1, 1) + timedelta(days=buf.read_formated("H"))

    @classmethod
    def write(cls, buf: Buffer, value):
        buf.write_formated("H", (value - date(1970, 1, 1)).days)


T = TypeVar("T")


class Nullable(Generic[T]):
    def __init__(self, inner_type: TypeProto):
        self.inner_type = inner_type

    @classmethod
    def __class_getitem__(cls, inner_type: Type[TypeProto]):
        return cls(inner_type)

    def read(self, buf: Buffer) -> T | None:
        is_null = buf.read_formated("b")
        if is_null:
            return None

        return self.inner_type.read(buf)

    def write(self, buf: Buffer, value: T | None) -> None:
        if value is None:
            buf.write_formated("b", 1)
            return
        buf.write_formated("b", 0)
        self.inner_type.write(buf, value)
