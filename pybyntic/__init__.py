"""
PyByntic extends Pydantic with binary-typed fields and automatic byte-level serialization.
Define models using familiar Pydantic syntax and turn them into compact binary payloads
with full control over layout and numeric precision.
"""
__version__ = "0.1.2"

from pybyntic.annotated_base_model import AnnotatedBaseModel
from pybyntic.types import *

__all__ = ["AnnotatedBaseModel"]
