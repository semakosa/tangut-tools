WARNING: This document is AI-generated from the codebase. I include it here for convenience, but it may contain inaccuracies and should not be used as a definitive reference.

# FST Structure Validation and Visualization

This document provides a detailed guide to using the FST structure validation and visualization features in TgtOrtho. These tools help ensure that your FST definitions are consistent and properly map features to components.

## Overview

The FST (Finite State Transducer) is a core component of TgtOrtho that handles the mapping between orthographic forms and phonological features. The validation tools help you:

1. Ensure consistent separator counts in FST definitions
2. Map FST variables to the features they handle
3. Validate entry points for parsing and generation
4. Visualize the structure of the FST for easier understanding

## Key Requirements for FST Definitions

When defining FST structures for orthography models, ensure that:

1. **All union branches must have the same separator count**: For any variable with a `union` definition, all branches must have the same total number of separators (`*` characters). This ensures consistent feature mapping regardless of which branch is taken.

2. **Entry points must have the correct separator count**: The entry point variables for parsing and generation should have exactly `len(keys) - 1` total separators, where `keys` is the list of feature names.

3. **Components should follow a consistent structure**: For clearest feature mapping, arrange components in a logical order that corresponds to the feature order.

## Using the Validation Tools

### Getting FST Structure Analysis

```python
from tgtortho.models import GX202411Orthography

# Enable debug mode for detailed logging
GX202411Orthography.set_debug_mode(True)

# Get the FST structure analysis
fst_analysis = GX202411Orthography.debug_fst_structure()

# Access specific information
direct_separators = fst_analysis["direct_separator_counts"]
total_separators = fst_analysis["total_separator_counts"]
feature_mappings = fst_analysis["feature_paths"]
warnings = fst_analysis["warnings"]

# Check specific variable
print(f"Syllable has {total_separators['Syllable']} total separators")
print(f"Features for InitialGradeAndVowel: {', '.join(feature_mappings['InitialGradeAndVowel'])}")
```

### Visualizing FST Structure

```python
# Generate a human-readable visualization
visualization = GX202411Orthography.visualize_fst_structure()
print(visualization)
```

The visualization includes:
- Entry points with their separator counts and expected counts
- Feature keys in their indexed order
- Components in order of appearance in the entry point definition
- Feature mappings for each component
- Separator counts (direct and indirect) for each component
- List of unmapped variables
- Any warnings detected during validation

## Example Visualization

```
FST Structure Visualization:
==============================

Entry Points:
  Parse: Syllable (expected: 9 total separators, actual: 9)
    Features: 卷舌冠音, 鼻冠音, 声母, 合口, 等, 元音, 韵尾, 卷舌, 紧, 声调
  Generate: Syllable (expected: 9 total separators, actual: 9)
    Features: 卷舌冠音, 鼻冠音, 声母, 合口, 等, 元音, 韵尾, 卷舌, 紧, 声调

Feature Keys:
  0: 卷舌冠音
  1: 鼻冠音
  2: 声母
  3: 合口
  4: 等
  5: 元音
  6: 韵尾
  7: 卷舌
  8: 紧
  9: 声调

FST Component Structure:
  Syllable: → All features
  └─ RetroflexPreinitial: 0 total separators
     Features: 卷舌冠音
  └─ InitialGradeAndVowel: 4 total separators (3 direct, 1 indirect)
     Features: 鼻冠音, 声母, 合口, 等, 元音
  └─ Coda: 0 total separators
     Features: 韵尾
  └─ Retroflex: 0 total separators
     Features: 卷舌
  └─ Tenseness: 0 total separators
     Features: 紧
  └─ Tone: 0 total separators
     Features: 声调

Unmapped Variables:
  InvariantInitial: 0 total separators
  InvariantInitialWithNasal: 0 total separators
  PreinitialUvularInitial: 1 total separators
  PreinitialVelarInitial: 1 total separators
  Rounding: 0 total separators
  UvularInitial: 0 total separators
  UvularInitialWithNasal: 0 total separators
  VelarInitial: 0 total separators
  VelarInitialWithNasal: 0 total separators
  VelarVowel: 0 total separators
  Vowel: 0 total separators
```

## Interpreting the Visualization

### Entry Points
Shows the main entry points for parsing and generation, their expected and actual separator counts, and the features they map to.

### Feature Keys
Lists all feature keys in order, with their index positions.

### FST Component Structure
Shows the main components of the FST in their order of appearance, with:
- Total separator counts (and breakdown of direct vs. indirect)
- Features mapped to each component

### Unmapped Variables
Lists variables without explicit feature mappings, which typically are subcomponents used within main components.

## Common Issues and Solutions

### Inconsistent Separator Counts in Union Branches

Problem:
```
Error in recursive analysis of 'Component': Inconsistent total separator count in union branches of Component: [1, 2]
```

Solution: Ensure all branches in the union have the same number of separators. For example:

```python
# Incorrect - inconsistent separators
'Component': {
    'union': [
        {'concat': ['A', '*', 'B']},  # 1 separator
        {'concat': ['C', '*', 'D', '*', 'E']}  # 2 separators
    ]
}

# Correct - consistent separators
'Component': {
    'union': [
        {'concat': ['A', '*', 'B']},  # 1 separator
        {'concat': ['C', '*', 'D']}  # 1 separator
    ]
}
```

### Incorrect Separator Count in Entry Point

Problem:
```
Warning: Parse entry point 'Syllable' has 8 total separators, but should have 9 for 10 keys
```

Solution: Ensure your entry point has exactly `len(keys) - 1` separators:

```python
# keys = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
# Should have 4 separators for 5 keys

# Incorrect - not enough separators
'Syllable': {
    'concat': ['Comp1', '*', 'Comp2', '*', 'Comp3']  # Only 2 separators
}

# Correct - 4 separators for 5 keys
'Syllable': {
    'concat': ['Comp1', '*', 'Comp2', '*', 'Comp3', '*', 'Comp4', '*', 'Comp5']
}
```

## Advanced Techniques

### Custom Feature Mapping

For complex FST structures where the automatic feature mapping doesn't produce desired results, you can integrate additional logic in your model implementation.

The `validate_fst_structure` function in `orthography.py` provides the core mapping logic and can be extended for custom needs.

### Debugging Complex FSTs

For complex FSTs, enable debug mode to see detailed logging information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug mode
YourOrthographyClass.set_debug_mode(True)

# Get analysis
analysis = YourOrthographyClass.debug_fst_structure()
```

The logs will show detailed information about the recursive separator counting and feature mapping process.

## Further Reading

- [Parsing and Generation](PARSING_AND_GENERATION.md) - More details on the parsing system
- [Model Specification](MODEL_SPECIFICATION.md) - How to define your own models 