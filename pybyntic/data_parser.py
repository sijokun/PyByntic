import typing as tp
from types import GenericAlias

from pybyntic.buffer import Buffer


class DataParser:
    def __init__(self, data: bytes) -> None:
        self.buf = Buffer(data)

    def read(self, field: tp.Any) -> tp.Any:
        if isinstance(field, GenericAlias) and field.__origin__ is list:
            list_len = self.buf.read_varint()
            value = []
            for i in range(list_len):
                value.append(self.read(field.__args__[0]))
            return value
        value = field.read(self.buf)
        return value
