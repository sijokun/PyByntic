import typing as tp
from types import GenericAlias

import typing_extensions as te
from pydantic import BaseModel

from pybyntic.data_dumper import DataDumper
from pybyntic.data_parser import DataParser
from pybyntic.types import Skip


class AnnotatedBaseModel(BaseModel):
    @classmethod
    def deserialize(cls, data: bytes, decoder: tp.Callable = None) -> te.Self:
        if decoder:
            data = decoder(data)
        parsed = {}
        parser = DataParser(data)
        for name, field in cls._get_types():
            value = parser.read(field)
            parsed[name] = value

        # Handle Skip fields - they should not be deserialized but need default values
        for name, model_field in cls.model_fields.items():
            if model_field.metadata and model_field.metadata[0] is Skip:
                if model_field.default is not None:
                    parsed[name] = model_field.default
                elif model_field.default_factory is not None:
                    parsed[name] = model_field.default_factory()
                else:
                    parsed[name] = None
        parsed = cls._fix_nested(parsed)
        return cls(**parsed)

    def serialize(self, encoder: tp.Callable = None) -> bytes:
        dumper = DataDumper()
        for name, field in self._get_types():
            data = self._get_field(name)
            dumper.dump(field, data)

        value = dumper.get_value()
        if encoder:
            value = encoder(value)
        return value

    @classmethod
    def _get_types(cls) -> list[tuple[str, type[tp.Any]]]:
        model_types = []
        for name, model_field in cls.model_fields.items():
            annotation = model_field.annotation

            # Check for list-like types
            if isinstance(annotation, GenericAlias) and annotation.__origin__ is list:
                element_type = annotation.__args__[0]
                if issubclass(element_type, AnnotatedBaseModel):
                    for field_name, field_type in element_type._get_types():
                        model_types.append((name + "." + field_name, list[field_type]))  # type: ignore
                else:
                    model_types.append((name, model_field.metadata[0]))
            elif isinstance(annotation, type) and issubclass(
                annotation, AnnotatedBaseModel
            ):
                for field_name, field_type in annotation._get_types():
                    model_types.append((name + "." + field_name, field_type))
            elif model_field.metadata[0] is not Skip:
                model_types.append((name, model_field.metadata[0]))
        return model_types

    def _get_values(self) -> tp.Any:
        values = {}
        for name, field in self._get_types():
            values[name] = getattr(self, name)
        return values

    @classmethod
    def _normalize_lists(
        cls,
        node: tp.Any,
        path: tuple[str, ...] = (),
        *,
        zip_single_key: bool = False,  # set True if you DO want single-key zipping
    ) -> tp.Any:
        if isinstance(node, list):
            return [
                cls._normalize_lists(x, path, zip_single_key=zip_single_key)
                for x in node
            ]

        # Dicts: normalize children first
        if isinstance(node, dict):
            for k in list(node.keys()):
                node[k] = cls._normalize_lists(
                    node[k], path + (k,), zip_single_key=zip_single_key
                )

            # If all children are lists and (we allow single-key OR there are 2+ keys), zip into list[dict]
            if node:  # non-empty
                values = list(node.values())
                if all(isinstance(v, list) for v in values) and (
                    zip_single_key or len(node) > 1
                ):
                    lengths = {len(v) for v in values}
                    if len(lengths) != 1:
                        where = ".".join(path) or "<root>"
                        raise ValueError(
                            f"Arrays under '{where}' have mismatched lengths: {lengths}"
                        )
                    n = lengths.pop()

                    zipped: list[dict[str, tp.Any]] = []
                    # build entries by taking i-th element from each list
                    for i in range(n):
                        entry = {k: node[k][i] for k in node.keys()}
                        entry = cls._normalize_lists(
                            entry, path + (f"[{i}]",), zip_single_key=zip_single_key
                        )
                        zipped.append(entry)
                    return zipped

            return node

        return node

    @classmethod
    def _fix_nested(cls, original_dict: dict[str, tp.Any]) -> dict[str, tp.Any]:
        root: dict[str, tp.Any] = {}

        for key, value in original_dict.items():
            if "." not in key:
                # plain key lives at root level
                root[key] = value
                continue
            parts = key.split(".")
            d = root
            for p in parts[:-1]:
                d = d.setdefault(p, {})
                if not isinstance(d, dict):
                    # Safety: if something else already sits here, override with a dict
                    d = {}
            d[parts[-1]] = value
        # Recursively normalize: zip sibling lists, and descend into children
        return cls._normalize_lists(root)

    @staticmethod
    def _list_of_dicts_to_dict_of_lists(list_of_dicts):
        if not list_of_dicts:
            return {}

        # Initialize a dictionary to store lists of values
        dict_of_lists = {key: [] for key in list_of_dicts[0]}

        # Iterate over each dictionary in the list
        for d in list_of_dicts:
            for key, value in d.items():
                dict_of_lists[key].append(value)

        return dict_of_lists

    def _get_field(self, field_name: str) -> tp.Any:
        parts = field_name.split(".")

        def apply_part(value: tp.Any, part: str) -> tp.Any:
            """Apply a single path component `part` to `value` recursively."""
            # If we have a nested iterable, map recursively over its elements
            if isinstance(value, (list, tuple, set)):
                return type(value)(apply_part(v, part) for v in value)

            # Dict support (optional)
            if isinstance(value, dict):
                return value[part]

            # Otherwise treat as an object with attributes
            return getattr(value, part)

        current = self
        for p in parts:
            current = apply_part(current, p)
        return current
