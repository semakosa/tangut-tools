"""
Phonological vector module.

This module provides the base classes and functions for creating phonological
vectors and orthography classes.

This is a compatibility module that imports from the core modules.
"""

from .core.phonology import PhonologicalVector, build_phonological_vector_class
from .core.orthography import build_orthography_class

__all__ = [
    'PhonologicalVector',
    'build_phonological_vector_class',
    'build_orthography_class',
] 