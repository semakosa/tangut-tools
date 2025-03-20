# TgtOrtho Documentation

Welcome to the TgtOrtho documentation. This directory contains comprehensive information on using and extending the TgtOrtho library.

## Documentation Files

- [Practical Guide](PRACTICAL_GUIDE.md) - Step-by-step examples for common tasks
- [Model Specification](MODEL_SPECIFICATION.md) - Technical details on model structure and implementation
- [Parsing and Generation](PARSING_AND_GENERATION.md) - In-depth explanation of the parsing system

## Core Concepts

TgtOrtho is built around a few key concepts:

### Phonological Vectors

Phonological vectors store feature values for each syllable according to a specific reconstruction model. These vectors validate that all feature combinations are valid according to the model's specification.

### Orthography Classes

Orthography classes provide parsing and generation functionality, transforming between string representations and phonological vectors. They use FST (Finite State Transducer) rules to define valid syllable structures.

### Debug Support

The library includes comprehensive debugging support to trace parsing and generation operations step-by-step, helping with troubleshooting and understanding complex operations.

## Getting Started

For new users, we recommend starting with the [Practical Guide](PRACTICAL_GUIDE.md) which provides examples for common tasks. For developers interested in extending the library with new models, refer to the [Model Specification](MODEL_SPECIFICATION.md) guide.

## Core Library Structure

The TgtOrtho library has the following structure:

- `tgtortho/core/` - Core classes and functions
  - `orthography.py` - Orthography class builder with debugging support
  - `phonology.py` - Phonological vector class builder
  - `fst.py` - Finite state transducer implementation
- `tgtortho/models/` - Reconstruction model implementations
  - `xun2024_11.py` - Xun Gong's November 2024 model
  - `xun2024_04.py` - Xun Gong's April 2024 model
  - `ghc.py` - Gong Hwang-cherng's model

See the [main README](../README.md) for additional information about the library. 