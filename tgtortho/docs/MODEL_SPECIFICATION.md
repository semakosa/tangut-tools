WARNING: This document is AI-generated from the codebase. I include it here for convenience, but it may contain inaccuracies and should not be used as a definitive reference.

# Creating Specification and Orthography Files

This document explains how to create custom specification and orthography files for the Tangut Tools library. These files define how phonological features are represented and how they map to orthographic (written) forms.

## 1. Phonological Specification

A phonological specification defines the feature space and valid values for a specific reconstruction model.

### 1.1 Basic Structure

```python
your_model_specification = {
    'reconstruction_id': "your_model_id",
    'specification': {
        'feature1': ["value1", "value2", ...],
        'feature2': ["value1", "value2", ...],
        # Add more features as needed
    }
}
```

### 1.2 Required Fields

- `reconstruction_id`: A unique identifier for your reconstruction model (e.g., "xun202408")
- `specification`: A dictionary mapping feature names to lists of valid values

### 1.3 Common Features

While you can define any features relevant to your reconstruction, these are common ones used in Tangut:

- Initials/Consonants (`声母`)
- Vowel (`元音`)
- Tone (`声调`)
- Grade (`等`)
- Coda/Final (`韵尾`)
- Tenseness (`紧`)
- Labialization (`合口`)
- Retroflexion (`卷舌`)
- Pre-initials (`卷舌冠音`, `鼻冠音`)

### 1.4 Example

```python
example_specification = {
    'reconstruction_id': "example",
    'specification': {
        '声母': ['p', 'ph', 'b', 'm', 't', 'th', 'd', 'n', 'k', 'kh', 'g', 'ŋ'],
        '元音': ['a', 'i', 'u', 'e', 'o'],
        '韵尾': ['', 'w', 'N'],
        '声调': ['平', '上']
    }
}
```

## 2. Orthography Definition

The orthography definition maps between orthographic representations (written forms) and phonological vectors (feature bundles) using Finite State Transducers (FSTs).

### 2.1 Basic Structure

```python
your_model_orthography = {
    'fst': {
        # FST definitions
    },
    'substitutions': [
        # Substitution pairs
    ],
    'keys': ['feature1', 'feature2', ...],
    'parse': 'EntryPoint',
    'generate': 'EntryPoint'
}
```

### 2.2 Required Fields

- `fst`: A dictionary defining finite-state transducer (FST) rules
- `substitutions`: A list of (easy, hard) pairs for text substitutions
- `keys`: A list of feature names in the order they should be processed
- `parse`: The FST entry point for parsing strings into feature vectors
- `generate`: The FST entry point for generating strings from feature vectors

### 2.3 The FST Section in Detail

The `fst` section uses a custom minilanguage to define finite-state transducers (FSTs). These define the mapping between orthographic representations and phonological features.

#### 2.3.1 Basic FST Elements

1. **String Literals**:
   - `"abc"` - Match the string "abc"
   - `"a:b"` - Convert "a" to "b" when parsing (and "b" to "a" when generating)

2. **Variable References**:
   - `"VarName"` - Reference another FST definition from the same `fst` dictionary

3. **Operations**:
   - `"union"` - Combine multiple FSTs with logical OR (any of the patterns can match)
   - `"concat"` - Concatenate multiple FSTs in sequence (must match in order)
   
4. **Special Symbols**:
   - `"*"` - Feature separator (used internally during processing)

#### 2.3.2 Building FST Rules

FST rules are defined hierarchically. You typically define simple patterns first, then combine them into more complex patterns.

```python
'fst': {
    # Simple patterns
    "Vowel": {
        "union": ["a", "i", "u", "e", "o"]
    },
    "Initial": {
        "union": ["p", "t", "k", "m", "n"]
    },
    "Tone": {
        "union": ["1:平", "2:上"]
    },
    
    # Combined pattern (the entry point)
    "Syllable": {
        "concat": ["Initial", "*", "Vowel", "*", "Tone"]
    }
}
```

In this example:
- We define three simple patterns: `Vowel`, `Initial`, and `Tone`
- We then create a `Syllable` pattern that concatenates them in sequence
- The `*` separators mark the boundaries between different features

### 2.4 Substitutions

The `substitutions` list defines text replacements applied before/after FST processing:

```python
'substitutions': [
    ('1', "¹"),  # Replace '1' with '¹' in output
    ('2', "²"),  # Replace '2' with '²' in output
    ('N', "ṁ")   # Replace 'N' with 'ṁ' in output
]
```

For each pair `(easy, hard)`:
- In generation: "easy" is replaced with "hard" in the output
- In parsing: "hard" is replaced with "easy" in the input

### 2.5 Optional: `substitutions_parse`

For more complex parsing rules, you can define a separate `substitutions_parse` list that uses regular expressions for more flexible text matching during parsing:

```python
'substitutions_parse': [
    ('1', "¹"),
    ('2', "²"),
    ('R', '^r')  # Match 'r' at the beginning of the string using regex
]
```

### 2.6 The `keys` List

The `keys` list specifies the order of features used in concatenation:

```python
'keys': ['声母', '元音', '韵尾', '声调']
```

This must match:
1. The fields in your specification
2. The order used in your FST concatenation rules

### 2.7 Complete Example

```python
example_orthography = {
    'fst': {
        "Initial": {
            "union": ["p", "t", "k", "m", "n"]
        },
        "Vowel": {
            "union": ["a", "i", "u", "e", "o"]
        },
        "Coda": {
            "union": ["", "w", "N"]
        },
        "Tone": {
            "union": ["1:平", "2:上"]
        },
        "Syllable": {
            "concat": ["Initial", "*", "Vowel", "*", "Coda", "*", "Tone"]
        }
    },
    'substitutions': [
        ('1', "¹"),
        ('2', "²"),
        ('N', "ṁ")
    ],
    'keys': ['声母', '元音', '韵尾', '声调'],
    'parse': 'Syllable',
    'generate': 'Syllable'
}
```

## 3. Advanced FST Techniques

For more complex reconstructions, you may need more sophisticated FST rules.

### 3.1 Feature Conditioning

Conditional patterns based on features:

```python
"InitialGradeAndVowel": {
    "union": [
        {"concat": ["Initial", "*", ":1", "*", "Vowel"]},  # Grade 1
        {"concat": ["Initial", "*", "a:2", "*", "Vowel"]}, # Grade 2 (maps 'a' to '2')
        {"concat": ["Initial", "*", ":3", "*", "Vowel"]}   # Grade 3
    ]
}
```

This defines three different patterns based on the grade feature (1, 2, or 3).

### 3.2 Context-dependent Mapping

Select between rule sets based on a feature's value:

```python
"PreinitialUvularInitial": {
    "union": [
        {"concat": [':-', '*', 'UvularInitial']},            # No preinitial
        {"concat": [':+', '*', 'UvularInitialWithNasal']}    # With preinitial
    ]
}
```

This selects between different initial sets based on whether a pre-initial is present.

### 3.3 Complex Substitutions with Regex

For parsing complex orthographic conventions:

```python
'substitutions_parse': [
    ('Rr', 'R[aeiouəw]'),  # Match 'R' followed by any vowel
    ('R', '^r'),           # Match 'r' at the beginning of the string
    ('_', '[̱̠]'),          # Match either of these diacritics
]
```

## 4. Creating and Using Your Model

Once you've defined your specification and orthography, you can create the associated classes:

```python
from tgtortho.phonology import build_phonological_vector_class, build_orthography_class

# Create the vector class
Your_Model_Vector = build_phonological_vector_class(your_model_specification)

# Create the orthography class
Your_Model_Orthography = build_orthography_class(Your_Model_Vector, your_model_orthography)

# Add it to the models/__init__.py to make it available
```

## 5. Best Practices

### 5.1 Development Process

1. **Start simple**: Begin with a minimal set of features
2. **Incremental testing**: Test your FST rules with simple examples before adding complexity
3. **Modular design**: Build complex patterns from simpler components
4. **Test bidirectional mapping**: Ensure parsing and generation work correctly

### 5.2 Common Pitfalls

1. **Overlapping rules**: Be careful with rules that could match the same input
2. **Missing feature values**: Ensure all features in `keys` are included in your FSTs
3. **Substitution order**: Most specific substitutions should come first
4. **Feature ordering**: The order in `keys` must match the order in your FST rules

### 5.3 Debugging Tips

1. **Test simple cases first**: Verify basic functionality before testing complex cases
2. **Check substitutions**: Ensure your substitutions are working as expected
3. **Inspect intermediate results**: Print intermediate values during processing
4. **Validate all paths**: Test all possible feature combinations

## 6. Real-World Example

Here's a simplified excerpt from the Xun2024_08 model demonstrating more complex patterns:

```python
xun2024_08_orthography = {
    'fst': {
        "RetroflexPreinitial": {
            "union": [":-", "R:+"]
        },
        "Vowel": {
            "union": ["i", "e", "ə", "u", "a", "o"]
        },
        "Coda": {
            "union": ["", "N", "w"]
        },
        "Tone": {
            "union": ["1:平", "2:上"]
        },
        "Syllable": {
            "concat": ["RetroflexPreinitial", "*", /* other components */, "*", "Tone"]
        }
    },
    'substitutions': [
        ('R', 'r'),
        ('N', "ṁ"),
        ('1', "¹"),
        ('2', "²"),
    ],
    'keys': ['卷舌冠音', /* other features */, '声调'],
    'parse': 'Syllable',
    'generate': 'Syllable'
}
```

## 7. Summary

Creating specification and orthography files involves:

1. **Defining phonological features** in your specification
2. **Creating FST rules** to map between written forms and feature values
3. **Specifying substitutions** for handling orthographic conventions
4. **Building the model classes** using the library's builder functions

By following this guide, you can create custom models for different Tangut reconstruction systems, or adapt the framework for other writing systems. 