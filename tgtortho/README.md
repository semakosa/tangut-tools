# TgtOrtho - Tangut Orthography Library

A comprehensive Python library for processing Tangut orthography and phonological representations. TgtOrtho provides robust tools for working with multiple reconstructions of Tangut phonology and seamlessly converting between different representation formats.

## Features

- Rigorous phonological vector representation with validation
- Deterministic orthographic parsing and generation
- Multiple cross-compatible reconstruction models
- Extensible architecture for custom reconstruction schemes
- Comprehensive debugging capabilities
- Advanced FST structure validation and visualization

## Dependencies

TgtOrtho has the following dependencies:

- **Python:** 3.6 or higher
- **Pyfoma:** 1.0.0 or higher - A Python library for finite state transducers, used for parsing and generation of orthographic forms
- **PyICU:** (optional) - For enhanced Unicode handling in complex scripts
- **NumPy:** (optional) - For numerical processing of phonological vectors in advanced use cases

For development:
- **pytest:** For running the test suite
- **sphinx:** For building documentation

## Installation

### From GitHub

```bash
# Install directly from GitHub
pip install git+https://github.com/semakosa/tangut-tools.git#subdirectory=tgtortho
```

### Local Development Installation

```bash
git clone https://github.com/semakosa/tangut-tools.git
cd tangut-tools/tgtortho
pip install -e .
```

## Basic Usage

```python
from tgtortho.models import GX202411Orthography

# Parse syllable into phonological vector
syllable = GX202411Orthography("tśhə¹")

# Access phonological features
print(syllable['声母'])  # tśh
print(syllable['元音'])  # ə 
print(syllable['声调'])  # 平

# Modify features
syllable['声调'] = '上'
print(syllable)  # tśhə²

# Parse multiple syllables
syllables = GX202411Orthography.parse_all("tśhə¹ kha²")
for syl in syllables:
    print(syl)
```

## Included Tools and Scripts

TgtOrtho comes with several useful scripts to help you get started and explore the functionality:

### Example Script

The `example.py` script demonstrates the core functionality of TgtOrtho, including parsing, feature access, modification, and debugging. Run it to see a live demonstration:

```bash
cd tangut-tools/tgtortho
python example.py
```

This script is also an excellent reference for learning how to use the library's various features.

### FST Validation Tool

The `test_fst_validation.py` script demonstrates how to use the FST validation features to analyze and debug the structure of finite-state transducers:

```bash
cd tangut-tools/tgtortho
python test_fst_validation.py
```

This tool helps you:
- Validate the consistency of your FST definitions
- Visualize the structure of FSTs and their feature mappings
- Debug parsing and generation processes
- Ensure proper mapping between phonological features and FST components

### Tangut Explorer GUI

The `tangut_explorer.py` script provides a graphical user interface (GTK4) for interactively exploring the different reconstruction models and orthographies:

```bash
cd tangut-tools/tgtortho
python tangut_explorer.py
```

With this GUI tool, you can:
- Select different reconstruction models
- Experiment with various orthographic representations
- Modify phonological features and see the resulting syllables in real time
- Learn about the structure of the different phonological systems

### Test Suite

TgtOrtho includes a comprehensive test suite to ensure correctness. Run the tests using:

```bash
cd tangut-tools/tgtortho
python run_tests.py
```

Or alternatively:

```bash
cd tangut-tools/tgtortho
pytest tests/
```

## Debugging Support

TgtOrtho provides comprehensive debugging capabilities for tracing parsing and generation processes:

```python
import logging
from tgtortho.models import GX202411Orthography

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Enable debugging for all instances of a class
GX202411Orthography.set_debug_mode(True)

# Or enable debugging for a specific instance
syllable = GX202411Orthography("tśhə¹", debug=True)

# Get detailed feature breakdown
syllable.debug_features()

# Debug multiple syllable parsing
debug_syllables = GX202411Orthography.parse_all("tśhə¹ kha²", debug=True)

# Analyze and visualize FST structure
fst_analysis = GX202411Orthography.debug_fst_structure()
visualization = GX202411Orthography.visualize_fst_structure()
print(visualization)
```

## FST Structure Validation

TgtOrtho includes advanced FST validation capabilities to ensure consistent and accurate parsing and generation:

```python
from tgtortho.models import GX202411Orthography

# Get detailed FST structure analysis
fst_analysis = GX202411Orthography.debug_fst_structure()

# Print a human-readable visualization
visualization = GX202411Orthography.visualize_fst_structure()
print(visualization)
```

The FST validation performs several checks:
- Ensures all union branches within a variable have the same number of separators
- Verifies that entry points have the correct number of separators for the given features
- Maps FST components to the features they handle based on their position
- Identifies potential inconsistencies or issues in the FST structure

When implementing your own FST-based parser, ensure that:
1. Each union branch in a variable has the same total separator count
2. The entry point has exactly `len(keys) - 1` separators
3. Component variables are properly structured for consistent feature mapping

## Available Reconstruction Models and Orthographies

- **GHC** - Gong Hwang-cherng's reconstruction: standard and machine orthographies
- **GX202411** - Xun Gong's reconstruction (November 2024): standard and IPA orthographies
- **GX202404** - Xun Gong's reconstruction (April 2024): standard and IPA orthographies

## Documentation

For more detailed information, please refer to the following documentation:

- [Practical Guide](docs/PRACTICAL_GUIDE.md) - Step-by-step examples and use cases
- [Model Specification](docs/MODEL_SPECIFICATION.md) - Details on model structure and implementation
- [Parsing and Generation](docs/PARSING_AND_GENERATION.md) - Technical details of the parsing system
- [FST Validation](docs/FST_VALIDATION.md) - Guide to validating and debugging FST structures

## Implementing Custom Models

Create new reconstruction models by defining specifications in the `tgtortho/models` directory:

```python
from tgtortho.core import build_phonological_vector_class, build_orthography_class

# Define phonological specification
my_model_specification = {
    'reconstruction_id': "my_model",
    'specification': {
        # Feature definitions
    }
}

# Create vector class
MyModelVector = build_phonological_vector_class(my_model_specification)

# Define orthography rules
my_model_orthography = {
    'fst': {
        # FST rules for parsing/generation
        # Note: Ensure all union branches within a variable have the same separator count
        'Syllable': {
            'concat': ['Component1', '*', 'Component2', '*', 'Component3']
        },
        'Component1': {...},
        'Component2': {
            'union': [
                {'concat': ['SubComp1', '*', 'SubComp2']},  # 1 separator
                {'concat': ['OtherComp', '*', 'AnotherComp']}  # Also 1 separator
            ]
        }
    },
    'substitutions': [
        # Character substitution rules
    ],
    'keys': ['feature1', 'feature2', ...],
    'parse': 'Syllable',
    'generate': 'Syllable'
}

# Create orthography class
MyModelOrthography = build_orthography_class(MyModelVector, my_model_orthography)

# Validate FST structure
print(MyModelOrthography.visualize_fst_structure())
```

See [Model Specification](docs/MODEL_SPECIFICATION.md) for detailed implementation guidance.

## License

This project is part of the Tangut Tools repository and is licensed under the MIT License. The orthography models are considered as part of the code and are licensed under the MIT License.

## Contact

For questions, permission requests, or collaboration opportunities, please contact:

- **Xun Gong**
- **University of Vienna**
- **Email:** xun.gong@univie.ac.at 