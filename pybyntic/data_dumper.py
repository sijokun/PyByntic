from typing import get_args, get_origin

from pybyntic.buffer import Buffer


class DataDumper:
    def __init__(self) -> None:
        self.buf = Buffer(b"")

    def dump(self, field_type, value):
        def _dump(ft, v):
            origin = get_origin(ft)

            # Handle list[...] (works for list[T], list[list[T]], etc.)
            if origin is list:
                (elem_t,) = get_args(ft)
                self.buf.write_varint(len(v))
                for item in v:
                    _dump(elem_t, item)
                return

            # Leaf type: delegate to the type's writer
            ft.write(self.buf, v)

        _dump(field_type, value)

    def get_value(self):
        return bytes(self.buf.buffer)
