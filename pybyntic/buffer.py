import struct
from typing import Any

import leb128  # type: ignore


# Thx to AsyncCH for the Buffer class
class Buffer:
    def __init__(self, data: bytes):
        self.buffer = bytearray(data)

    def _is_buffer_empty(self) -> bool:
        return len(self.buffer) == 0

    def is_buffer_readable(self) -> bool:
        if len(self.buffer) == 0:
            return False
        return True

    def _read_one(self) -> int:
        packet = self.buffer[:1]
        self.buffer = self.buffer[1:]
        return packet[0]

    def read_varint(self) -> int:
        packets = bytearray()
        while True:
            if not (self.is_buffer_readable()):
                break
            packet = self._read_one()
            packets.append(packet)
            if packet < 0x80:
                break
        return leb128.u.decode(packets)  # type: ignore

    def read_bytes(self, length: int) -> bytearray:
        packets = bytearray()

        while length > 0:
            if not (self.is_buffer_readable()):
                break
            packet = self.buffer[:1]
            packets.extend(packet)
            self.buffer = self.buffer[1:]
            length -= 1
        return packets

    def read_fixed_str(
        self, length: int, as_bytes: bool = False, encoding: str = "utf-8"
    ) -> str | bytes:
        packet = self.read_bytes(length)
        if as_bytes:
            return packet
        return packet.decode(encoding=encoding)

    def read_str(self, as_bytes: bool = False, encoding: str = "utf-8") -> str | bytes:
        length = self.read_varint()
        return self.read_fixed_str(length=length, as_bytes=as_bytes, encoding=encoding)

    def read_formated(self, fmt: str) -> Any:
        s = struct.Struct("<" + fmt)
        packet = self.read_bytes(s.size)
        return s.unpack(packet)[0]

    def write_bytes(self, data: bytes) -> None:
        self.buffer.extend(data)

    def write_varint(self, value: int) -> None:
        packets = bytearray()

        while True:
            byte = value & 0x7F
            value >>= 7
            if value != 0:
                byte |= 0x80
            packets.append(byte)
            if value == 0:
                break
        self.buffer.extend(packets)

    def write_formated(self, fmt: str, value: Any) -> None:
        b = struct.pack(fmt, value)
        self.write_bytes(b)
