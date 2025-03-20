"""
Core modules for the tgtortho package.

This package contains the core functionality of the tgtortho package,
including the phonological vector and orthography classes.
"""

from .phonology import PhonologicalVector, build_phonological_vector_class
from .orthography import build_orthography_class

__all__ = [
    'PhonologicalVector',
    'build_phonological_vector_class',
    'build_orthography_class',
] 