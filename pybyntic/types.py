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
    pytype = bool

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
    def write(cls, buf: Buffer, value: int):
        hi = value >> 64
        lo = value & 0xFFFFFFFFFFFFFFFF
        buf.write_formated("Q", hi)
        buf.write_formated("Q", lo)


class String:
    """
    A variable-length string prefixed with its length as a VarInt.
    UTF-8 encoding is used.
    """

    @classmethod
    def read(cls, buf: Buffer) -> str:
        length = buf.read_varint()
        data = buf.read_fixed_str(length)
        return data

    @classmethod
    def write(cls, buf: Buffer, value: str):
        data = value.encode("utf-8")
        buf.write_varint(len(data))
        buf.write_bytes(data)


class FixedString:
    """
    A fixed-length string of N bytes (not characters).
    """

    def __init__(self, length: int, encoding: str = "utf-8"):
        assert length >= 1  # FixedString must have a length of at least 1

        self.length = length
        self.encoding = encoding

    @classmethod
    def __class_getitem__(cls, args: int | tuple[int, str]):
        if isinstance(args, tuple):
            length, encoding = args
            return cls(length, encoding)
        else:
            return cls(args)

    def read(self, buf: Buffer) -> str:
        data = buf.read_fixed_str(self.length, self.encoding)
        return data

    def write(self, buf: Buffer, value: str):
        data = value.encode(self.encoding)
        if len(data) > self.length:
            data = data[: self.length]
        elif len(data) < self.length:
            data += b"\x00" * (self.length - len(data))
        buf.write_bytes(data)


class StringJson:
    @classmethod
    def read(cls, buf: Buffer) -> dict[str, Any]:
        length = buf.read_varint()
        data = buf.read_fixed_str(length)
        return json.loads(data if data else "{}")

    @classmethod
    def write(cls, buf: Buffer, value: dict[str, Any]):
        data = json.dumps(value).encode()
        buf.write_varint(len(data))
        buf.write_bytes(data)


class DateTime32:
    @classmethod
    def read(cls, buf: Buffer) -> datetime:
        if not buf.is_buffer_readable():
            return ZERO_UTC

        return datetime.fromtimestamp(buf.read_formated("I"), tz=timezone.utc)

    @classmethod
    def write(cls, buf: Buffer, value: datetime):
        if value.utcoffset() is not None and value.utcoffset().total_seconds() > 0:
            raise ValueError("Use DateTime32TZ for timezone-aware datetime")
        value = value.astimezone(timezone.utc)
        ts = int(value.timestamp())
        if ts < 0 or ts > 2 ** 32 - 1:
            raise ValueError("DateTime value out of range for DateTime32, use DateTime64 instead")
        UInt32.write(buf, ts)


class DateTime32TZ:
    @classmethod
    def read(cls, buf: Buffer) -> datetime:
        timestamp = UInt32.read(buf)
        offset_minutes = Int16.read(buf)
        tz = timezone(timedelta(minutes=offset_minutes))
        return datetime.fromtimestamp(timestamp, tz=tz)

    @classmethod
    def write(cls, buf: Buffer, value: datetime):
        offset = int(value.utcoffset().total_seconds() / 60)
        ts = int(value.timestamp())
        if ts < 0 or ts > 2**32 - 1:
            raise ValueError("DateTime value out of range for DateTime32, use DateTime64 instead")
        UInt32.write(buf, ts)
        Int16.write(buf, offset)


class DateTime64:
    precision = 3

    def __init__(self, precision):
        self.precision = precision

    @classmethod
    def __class_getitem__(cls, precision=3):
        return cls(precision)

    def read(self, buf: Buffer) -> datetime:
        ticks = Int64.read(buf)

        divisor = 10**self.precision

        timestamp = ticks / divisor

        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def write(self, buf: Buffer, value: datetime):
        if value.utcoffset().total_seconds():
            raise ValueError("Use DateTime64TZ for timezone-aware datetime")
        divisor = 10**self.precision
        value = value.astimezone(timezone.utc)
        ticks = int(value.timestamp() * divisor)
        Int64.write(buf, ticks)


class DateTime64TZ:
    precision = 3

    def __init__(self, precision):
        self.precision = precision

    @classmethod
    def __class_getitem__(cls, precision=3):
        return cls(precision)

    def read(self, buf: Buffer) -> datetime:
        ticks = Int64.read(buf)
        offset_minutes = Int16.read(buf)
        tz = timezone(timedelta(minutes=offset_minutes))

        divisor = 10**self.precision

        timestamp = ticks / divisor

        return datetime.fromtimestamp(timestamp, tz=tz)

    def write(self, buf: Buffer, value: datetime):

        divisor = 10**self.precision
        ticks = int(value.timestamp() * divisor)

        offset = int(value.utcoffset().total_seconds() / 60)
        Int64.write(buf, ticks)
        Int16.write(buf, offset)


class Date:
    @classmethod
    def read(cls, buf: Buffer) -> date:
        return date(1970, 1, 1) + timedelta(days=buf.read_formated("H"))

    @classmethod
    def write(cls, buf: Buffer, value: date):
        days = (value - date(1970, 1, 1)).days
        if days < 0 or days > 2**16 - 1:
            raise ValueError("Date value out of range for Date type")
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
