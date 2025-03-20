# FST Structure Validation

This feature validates the structure of Finite State Transducer (FST) definitions in orthography specifications, particularly focusing on the consistency of "*" separators which correspond to feature fields.

## Overview

The FST validation system:

1. Recursively counts "*" separators in FST definitions
2. Verifies consistency across union branches
3. Maps FST variables to feature fields
4. Validates that entry points cover all expected features

## Key Concepts

### Direct vs. Total Separators

- **Direct separators**: "*" tokens directly present in an FST variable definition
- **Total separators**: All separators in the path, including those in referenced variables

### Field Mapping

The system attempts to map FST variables to feature fields based on the number of separators:
- A variable with N total separators handles N+1 fields
- Entry points should have (len(keys) - 1) separators to cover all fields

## Using the Feature

### Checking FST Structure During Development

```python
from tgtortho.models import MyOrthographyClass

# Enable debug mode to see detailed logging
MyOrthographyClass.set_debug_mode(True)

# Get detailed analysis of FST structure
analysis = MyOrthographyClass.debug_fst_structure()

# Print human-readable visualization
visualization = MyOrthographyClass.visualize_fst_structure()
print(visualization)
```

### Visualization Example

```
FST Structure Visualization:
==============================

Entry Points:
  Parse: Syllable (expected: 9 total separators, actual: 9)
  Generate: Syllable (expected: 9 total separators, actual: 9)

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

FST Variables:
  Syllable: 9 total separators (5 direct, 4 indirect) → Fields: 卷舌冠音, 鼻冠音, 声母, 合口, 等, 元音, 韵尾, 卷舌, 紧, 声调 (PARSE ENTRY POINT)
  InitialGradeAndVowel: 4 total separators (3 direct, 1 indirect)
  PreinitialUvularInitial: 1 total separators
  PreinitialVelarInitial: 1 total separators
  [...]
```

## Troubleshooting

### Common Warnings

1. **Inconsistent separator count in union branches**:
   - All branches in a union should have the same number of separators
   - Fix: Ensure all branches have consistent structure

2. **Entry point has incorrect number of separators**:
   - The entry point should have (len(keys) - 1) total separators
   - Fix: Ensure the entry point variable connects all features with the right number of separators

### Fine-Tuning Model Definitions

When designing FST definitions:

1. Start with simple patterns with 0 separators
2. Combine them with separators to mark field boundaries
3. Use the visualization to ensure correct field mapping
4. Fix inconsistencies in union branches

## Implementation Details

The validation happens automatically when building orthography classes:

```python
YourOrthographyClass = build_orthography_class(YourVectorClass, your_orthography_spec)
```

The validation checks:
- Direct separator counts via `count_direct_separators()`
- Total separator counts via `count_total_separators()`
- Field mappings
- Entry point correctness

Results are stored in the class as `fst_analysis`. 