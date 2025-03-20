WARNING: This document is AI-generated from the codebase. I include it here for convenience, but it may contain inaccuracies and should not be used as a definitive reference.

# TgtOrtho: Parsing and Generation Processes

This document provides a comprehensive explanation of how the Tangut Orthography (TgtOrtho) library parses orthographic representations into phonological vectors and generates representations from these vectors. It explains the internal structures, fields, and processes involved in the conversion between orthographic and phonological representations.

## Table of Contents

- [Overview of the System](#overview-of-the-system)
- [Key Components](#key-components)
- [Parsing Process (String to Vector)](#parsing-process-string-to-vector)
- [Generation Process (Vector to String)](#generation-process-vector-to-string)
- [Phonological Vector Fields](#phonological-vector-fields)
- [Finite State Transducer (FST) System](#finite-state-transducer-fst-system)
- [Substitution Rules](#substitution-rules)
- [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)

## Overview of the System

The TgtOrtho library is designed to handle Tangut orthography and phonological representations. The system consists of three core components:

1. **Phonological Vectors**: Structured representations of phonological features
2. **Orthographic Systems**: Rules for mapping between text and phonological features
3. **Finite State Transducers (FSTs)**: The underlying mechanism for conversion

The library uses these components to:
- Parse orthographic strings (e.g., "tśhə¹") into phonological feature vectors
- Generate orthographic strings from phonological feature vectors
- Validate and manipulate phonological vectors

## Key Components

### PhonologicalVector Class

The `PhonologicalVector` class provides a foundation for representing phonological vectors. It:
- Stores feature values in a namedtuple
- Provides dictionary-like access to features (e.g., `vector['声母']`)
- Validates feature values against the specification
- Supports feature value updates with validation

### Orthography Class

The `Orthography` class (created by `build_orthography_class()`) handles:
- Parsing strings into phonological vectors
- Generating orthographic strings from vectors
- Batch parsing of multiple syllables

### FST Utilities

The FST utilities (in `core/fst.py`) provide:
- A minilanguage for defining finite state transducers
- Conversion between strings and phonological representations
- Bidirectional mapping functionality (parsing and generation)

## Parsing Process (String to Vector)

When you parse a string like "tśhə¹" into a phonological vector, the following steps occur:

1. **Initialization**: A new `Orthography` instance is created with the input string.

2. **Pre-processing**:
   - If `substitutions_parse` is defined, regex-based substitutions are applied to the input string.
   - Otherwise, simple text-based substitutions from `substitutions` are applied in reverse.

3. **FST Parsing**:
   - The preprocessed string is passed to the FST parser.
   - The FST identified by the `parse` key in the orthography specification is applied.
   - The parser attempts to match the string against the patterns defined in the FST.

4. **Feature Extraction**:
   - If parsing succeeds, the FST outputs a string with feature values separated by '*'.
   - These values are mapped to feature names according to the `keys` list.
   - The result is a dictionary mapping feature names to their values.

5. **Vector Creation**:
   - A namedtuple is created from the feature dictionary.
   - The namedtuple is validated against the phonological specification.
   - A `PhonologicalVector` instance is created using the validated namedtuple.

Example flow:
```
"tśhə¹" → Apply substitutions → FST parsing → "*tśh*-*-*3*ə**-*-*平"
  → Map to features → {'卷舌冠音': '-', '鼻冠音': '-', '声母': 'tśh', ...}
  → Create namedtuple → Create PhonologicalVector
```

## Generation Process (Vector to String)

When generating an orthographic string from a phonological vector, the process works in reverse:

1. **Feature Extraction**:
   - Feature values are extracted from the vector in the order specified by the `keys` list.
   - These values are joined with '*' separators to create a feature string.

2. **FST Generation**:
   - The feature string is passed to the FST generator.
   - The FST identified by the `generate` key in the orthography specification is applied.
   - The generator converts the feature string into an orthographic string.

3. **Post-processing**:
   - Text-based substitutions from the `substitutions` list are applied to the output string.
   - Each 'easy' token is replaced with its corresponding 'hard' token.

Example flow:
```
PhonologicalVector → Extract features → "*-*-*tśh*-*3*ə**-*-*平"
  → FST generation → "tśhə1" → Apply substitutions → "tśhə¹"
```

## Phonological Vector Fields

The specific fields in a phonological vector depend on the reconstruction model, but common fields include:

| Field Name | Description | Example Values | Notes |
|------------|-------------|----------------|-------|
| `卷舌冠音` | Retroflex pre-initial | `-`, `+` | Presence of a retroflex pre-initial consonant |
| `鼻冠音` | Nasal pre-initial | `-`, `+` | Presence of a nasal pre-initial |
| `声母` | Initial consonant | `p`, `tśh`, `k`, etc. | The main consonant at the beginning of a syllable |
| `合口` | Labialization | `-`, `+` | Presence of lip-rounding |
| `元音` | Vowel | `a`, `i`, `ə`, etc. | The main vowel of the syllable |
| `韵尾` | Coda | ``, `w`, `N` | Consonant or glide at the end of the syllable |
| `卷舌` | Retroflexion | `-`, `+` | Retroflexion of the syllable |
| `紧` | Tenseness | `-`, `+` | Tenseness of the syllable |
| `等` | Grade | `1`, `2`, `3` | Phonological grade (influences vowel quality) |
| `声调` | Tone | `平`, `上` | Tone category |

These field names are consistent across the codebase, though the valid values for each field may vary between reconstruction models.

## Finite State Transducer (FST) System

The FST system is the heart of the parsing and generation processes. It uses a custom minilanguage to define complex mapping rules between orthographic forms and feature representations.

### FST Minilanguage

The FST minilanguage supports the following elements:

1. **String Literals**:
   - `"abc"` - Match the exact string "abc"
   - `"a:b"` - Convert "a" to "b" during parsing and "b" to "a" during generation

2. **Variable References**:
   - `"VarName"` - Reference another FST definition

3. **Operators**:
   - `"union"` - Logical OR (any pattern can match)
   - `"concat"` - Concatenation (patterns must match in sequence)

4. **Feature Separator**:
   - `"*"` - Separates features in the internal representation

### FST Definition Example

```python
'fst': {
    "Vowel": {
        "union": ["a", "i", "u", "e", "o", "ə"]
    },
    "Initial": {
        "union": ["p", "t", "k", "tśh"]
    },
    "Tone": {
        "union": ["1:平", "2:上"]
    },
    "Syllable": {
        "concat": ["Initial", "*", "Vowel", "*", "Tone"]
    }
}
```

In this example:
- We define simple patterns for vowels, initials, and tones
- The `Syllable` pattern concatenates these components
- During parsing, a string like "tśhə1" would be converted to "tśh*ə*平"
- During generation, the reverse conversion occurs

## Substitution Rules

Substitution rules allow for text transformations before parsing and after generation:

### Standard Substitutions

```python
'substitutions': [
    ('1', "¹"),  # Replace '1' with '¹' in output
    ('2', "²"),  # Replace '2' with '²' in output
    ('N', "ṁ")   # Replace 'N' with 'ṁ' in output
]
```

For each pair `(easy, hard)`:
- In generation: The "easy" form is replaced with the "hard" form in the output
- In parsing: The "hard" form is replaced with the "easy" form in the input

### Regex-Based Parsing Substitutions

For more complex parsing patterns, the `substitutions_parse` option provides regex functionality:

```python
'substitutions_parse': [
    ('Rr', 'R[aeiouəw]'),  # Match 'R' followed by any vowel
    ('R', '^r'),           # Match 'r' at the beginning of a string
    ('_', '[̱̠]'),           # Match either diacritic
]
```

These are applied only during parsing and offer more powerful pattern matching.

## Common Issues and Troubleshooting

### Parsing Failures

If a string fails to parse, possible causes include:

1. **Unrecognized orthographic pattern**: The input doesn't match any pattern in the FST.
   - Solution: Check if the input follows the orthographic conventions of the selected model.

2. **Missing substitution rule**: A character or sequence in the input doesn't have a corresponding substitution.
   - Solution: Add appropriate substitution rules to the orthography specification.

3. **Invalid feature value**: Parsing succeeded, but a feature value is invalid according to the specification.
   - Solution: Ensure the specification includes all possible values for each feature.

### Generation Issues

If generation produces unexpected results:

1. **Wrong feature order**: The `keys` list doesn't match the order expected by the FST.
   - Solution: Ensure the `keys` list matches the FST's expected order.

2. **Substitution conflicts**: Multiple substitutions affecting the same text.
   - Solution: Order substitutions carefully, with more specific ones before general ones.

3. **FST ambiguity**: The FST can map the same feature set to multiple strings.
   - Solution: Refine the FST definition to reduce ambiguity.

---

*Note: This documentation is based on the current codebase. If you have specific questions or issues not covered here, please refer to the API documentation or open an issue in the repository.* 