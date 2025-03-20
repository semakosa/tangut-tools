WARNING: This document is AI-generated from the codebase. I include it here for convenience, but it may contain inaccuracies and should not be used as a definitive reference.

# TgtOrtho: Practical Usage Guide

This guide provides examples and instructions for using the TgtOrtho library effectively. It covers essential operations for processing Tangut orthography with practical code examples.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Working with Individual Syllables](#working-with-individual-syllables)
- [Working with Multiple Syllables](#working-with-multiple-syllables)
- [Accessing and Modifying Features](#accessing-and-modifying-features)
- [Debugging Functionality](#debugging-functionality)
- [Using Different Reconstruction Models](#using-different-reconstruction-models)
- [Creating Custom Models](#creating-custom-models)

## Installation

```bash
# For development installation
git clone https://github.com/semakosa/tangut-tools.git
cd tangut-tools/tgtortho
pip install -e .
```

## Basic Usage

Import a specific orthography model to parse Tangut syllables:

```python
from tgtortho.models import GX202411Orthography

# Parse a single syllable
syllable = GX202411Orthography("tśhə¹")
print(syllable)  # Output: tśhə¹

# Access phonological features
print(syllable['声母'])  # Output: tśh
print(syllable['元音'])  # Output: ə
print(syllable['声调'])  # Output: 平
```

## Working with Individual Syllables

### Parsing Syllables

When creating a syllable from a string, TgtOrtho:
1. Parses the string into phonological features
2. Creates a vector representation
3. Validates the feature combination

```python
from tgtortho.models import GX202411Orthography

syllable = GX202411Orthography("tśhə¹")
print(syllable)  # Output: tśhə¹
```

### Accessing Features

Access phonological features using dictionary-style notation:

```python
from tgtortho.models import GX202411Orthography

syllable = GX202411Orthography("tśhə¹")
print(syllable['声母'])  # Initial consonant: tśh
print(syllable['元音'])  # Main vowel: ə
print(syllable['声调'])  # Tone: 平
```

### Modifying Features

Modify phonological features using dictionary-style assignment:

```python
from tgtortho.models import GX202411Orthography

syllable = GX202411Orthography("tśhə¹")
print(syllable)  # tśhə¹

# Change tone
syllable['声调'] = '上'
print(syllable)  # tśhə²

# Change vowel
syllable['元音'] = 'a'
print(syllable)  # tśha²

# Add labialization
syllable['合口'] = '+'
print(syllable)  # tśhwa²
```

## Working with Multiple Syllables

Parse multiple syllables from a space-separated string:

```python
from tgtortho.models import GX202411Orthography

text = "tśhə¹ kha² lo¹ ma²"
syllables = GX202411Orthography.parse_all(text)

print(f"Number of syllables: {len(syllables)}")  # Output: 4

for i, syl in enumerate(syllables, 1):
    features = ", ".join([f"{k}: {v}" for k, v in syl.items() if k in ['声母', '元音', '声调']])
    print(f"Syllable {i}: {syl} ({features})")
```

## Accessing and Modifying Features

Phonological features correspond to the reconstruction model's feature set:

```python
from tgtortho.models import GX202411Orthography

syllable = GX202411Orthography("tśhə¹")

# List all features
for key, value in syllable.items():
    print(f"{key}: {value}")

# Update multiple features
syllable['声母'] = 'p'
syllable['元音'] = 'a'
syllable['声调'] = '上'
print(syllable)  # Output: pa²
```

## Debugging Functionality

TgtOrtho provides comprehensive debugging for parsing and generation processes:

### Enabling Debug Mode

```python
import logging
from tgtortho.models import GX202411Orthography

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Enable debugging for all class instances
GX202411Orthography.set_debug_mode(True)

# Parse with debugging enabled
syllable = GX202411Orthography("tśhə¹")
```

### Instance-Level Debugging

```python
# Debug specific instance only
syllable = GX202411Orthography("tśhə¹", debug=True)

# Get detailed feature breakdown
features = syllable.debug_features()

# Debug complex parsing
complex_syllable = GX202411Orthography("Rdzwəw²", debug=True)
```

### Debugging Multiple Syllables

```python
# Debug parse_all operation
debug_syllables = GX202411Orthography.parse_all("tśhə¹ kha² invalid ma²", debug=True)
```

## Using Different Reconstruction Models

TgtOrtho supports multiple reconstruction models that can be used interchangeably:

```python
from tgtortho.models import GX202411Orthography  # November 2024 version
from tgtortho.models import GX202404Orthography  # April 2024 version
from tgtortho.models import GhcOrthography      # Gong Hwang-cherng's

# Create syllables with different models
syl1 = GX202404Orthography("tśhiə¹")
syl2 = GX202411Orthography("tśhə¹")
syl3 = GhcOrthography("1ci")

print(syl1)  # Using April 2024 model
print(syl2)  # Using November 2024 model
print(syl3)  # Using Ghc model
```

## Creating Custom Models

To create a custom reconstruction model, define the phonological features and orthography rules:

1. Create a new file in `tgtortho/models/`
2. Define your phonological vector specification
3. Define your orthography rules
4. Build and export the classes

See [Model Specification](MODEL_SPECIFICATION.md) for detailed instructions on creating custom models and [Parsing and Generation](PARSING_AND_GENERATION.md) for information on the underlying system.

Refer to the [README](../README.md) for additional information about the library.

---

For more detailed technical information about the parsing and generation processes, please refer to the [Parsing and Generation Processes](PARSING_AND_GENERATION.md) documentation. 