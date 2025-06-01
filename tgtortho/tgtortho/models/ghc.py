"""
Gong-Hwang-Coblin (GHC) reconstruction.

This module provides classes for working with the Gong-Hwang-Coblin 
reconstruction of Tangut phonology.
"""

from tgtortho.phonology import build_phonological_vector_class, build_orthography_class

# Specification for the GHC model
ghc_specification = {
    'reconstruction_id': "ghc",
    'specification': {
        '声母': ['p', 't', 'ts', 'tś', 'k', 'ph', 'th', 'tsh', 'tśh', 'kh', 'b', 'd', 'dz', 'dź', 'g', 'm', 'n', 'ŋ', 's', 'ś', 'x', 'z', 'ź', 'ɣ', 'r', 'l', 'lh', 'ˑ', 'w'],
        '合口': ['-', '+'],
        '摄': ['u', 'i', 'iN', 'a', 'aN', 'ə', 'ij', 'əj', 'iw', 'o', 'ow', 'uN'],
        '卷舌': ['-', '+'],
        '紧': ['-', '+'],
        '长': ['-', '+'],
        '等': ['1', '2', '3'],
        '声调': ['平', '上']
    }
}

# Dynamically create a new class for GHC model
GhcVector = build_phonological_vector_class(ghc_specification)

ghc_orthography = {
    'fst': {
        "Initial": {
            "union": ["p", "t", "ts", "tś", "k",
                        "ph", "th", "tsh", "tśh", "kh",
                        "b", "d", "dz", "dź", "g",
                        "m", "n", "ŋ",
                        "s", "ś", "x",
                        "z", "ź", "ɣ",
                        "r", "l", "lh", "w", "ˑ"]
        },
        "Rounding": {
            "union": [":-", "w:+"]
        },
        "Grade3Vowel": {
            "union": ["i", "ɨ:ə"]
        },
        "Grade1Vowel": {
            "union": ["e:i", "ə"]
        },
        "NonGradedVowel": {
            "union": ["u", "a", "o"]
        },
        "Grade": {
            "union": [":1", "i:2", "j:3"]
        },
        "GradeAndVowel": {
            "union": [
                {"concat": ["Grade", "*", "Rounding", "*", "NonGradedVowel"]},
                {"concat": [":1", "*", "Rounding", "*", "Grade1Vowel"]},
                {"concat": ["i:2", "*", "Rounding", "*", "Grade1Vowel"]},
                {"concat": ["j:3", "*", "Rounding", "*", "Grade3Vowel"]}
            ]
        },
        "Tenseness": {
            "union": [":-", "·:+"]
        },
        "Length": {
            "union": [":-", "_:+"]
        },
        "Retroflex": {
            "union": [":-", "r:+"]
        },
        "Coda": {
            "union": ["", "N", "w", "j"]
        },
        "Tone (permissive)": {
            "union": ["1:平", "2:上", "?:平", "?:上"]
        },
        "Syllable (permissive)": {
            "concat": ["Initial", "*", "GradeAndVowel", "Coda", "*", 'Tenseness', '*', 'Length', '*', 'Retroflex', "*", "Tone (permissive)"]
        },
        "Tone (strict)": {
            "union": ["1:平", "2:上"]
        },
        "Syllable (strict)": {
            "concat": ["Initial", "*", "GradeAndVowel", "Coda", "*", 'Tenseness', '*', 'Length', '*', 'Retroflex', "*", "Tone (strict)"]
        },
    },
    'substitutions': [
        ('j_', '_j'),
        ('j·', '·j'),
        ('w·', '·w'),
        ('w_', '_w'),
        ("N", "~"),
        ("~", "̃"),
        ("a~", "ã"),
        ("i~", "ĩ"),
        ("e~", "ẽ"),
        ("o~", "õ"),
        ("u~", "ũ"),
        ('_', "̱"),
        ('a_', 'aa'),
        ('i_', 'ii'),
        ('u_', 'uu'),
        ('e_', 'ee'),
        ('o_', 'oo'),
        ('ə_', 'əə'),
        ('ɨ_', 'ɨɨ'),
        ('·', "."), # Foma does not support dot as a non-wildcard
        ('.', "̣"),
        ('1', "¹"),
        ('2', "²")],
    'keys': ['声母', '等', '合口', '摄', '紧', '长', '卷舌', '声调'],
    'parse': 'Syllable (permissive)',
    'generate': 'Syllable (strict)'
}

GhcOrthography = build_orthography_class(GhcVector, ghc_orthography)

ghc_machine_orthography = {
    'fst': {
        "Initial": {
            "union": ["p", "t", "ts", "tś", "k",
                        "ph", "th", "tsh", "tśh", "kh",
                        "b", "d", "dz", "dź", "g",
                        "m", "n", "ŋ",
                        "s", "ś", "x",
                        "z", "ź", "ɣ",
                        "r", "l", "lh", "w", "·:ˑ"]
        },
        "Rounding": {
            "union": [":-", "w:+"]
        },
        "Grade3Vowel": {
            "union": ["i", "ɨ:ə"]
        },
        "Grade1Vowel": {
            "union": ["e:i", "ə"]
        },
        "NonGradedVowel": {
            "union": ["u", "a", "o"]
        },
        "Grade": {
            "union": [":1", "i:2", "j:3"]
        },
        "GradeAndVowel": {
            "union": [
                {"concat": ["Grade", "*", "Rounding", "*", "NonGradedVowel"]},
                {"concat": [":1", "*", "Rounding", "*", "Grade1Vowel"]},
                {"concat": ["i:2", "*", "Rounding", "*", "Grade1Vowel"]},
                {"concat": ["j:3", "*", "Rounding", "*", "Grade3Vowel"]}
            ]
        },
        "Tenseness": {
            "union": [":-", ".:+"]
        },
        "Length": {
            "union": [":-", "_:+"]
        },
        "Retroflex": {
            "union": [":-", "r:+"]
        },
        "Coda": {
            "union": ["", "N", "w", "j"]
        },
        "Tone (permissive)": {
            "union": ["1:平", "2:上", "?:平", "?:上"]
        },
        "Syllable (permissive)": {
            "concat": ["Initial", "*", "GradeAndVowel", "Coda", "*", 'Tenseness', '*', 'Length', '*', 'Retroflex', "*", "Tone (permissive)"]
        },
        "Tone (strict)": {
            "union": ["1:平", "2:上"]
        },
        "Syllable (strict)": {
            "concat": ["Initial", "*", "GradeAndVowel", "Coda", "*", 'Tenseness', '*', 'Length', '*', 'Retroflex', "*", "Tone (strict)"]
        },
    },
    'substitutions': [
        ('j_', '_j'),
        ('j.', '.j'),
        ('w.', '.w'),
        ('w_', '_w'),
        ("N", "~"),
        ("a~", "ã"),
        ("i~", "ĩ"),
        ("e~", "ẽ"),
        ("o~", "õ"),
        ("u~", "ũ"),
        ('a_', 'aa'),
        ('i_', 'ii'),
        ('u_', 'uu'),
        ('e_', 'ee'),
        ('o_', 'oo'),
        ('ə_', 'əə'),
        ('ɨ_', 'ɨɨ')],
    'keys': ['声母', '等', '合口', '摄', '紧', '长', '卷舌', '声调'],
    'parse': 'Syllable (permissive)',
    'generate': 'Syllable (strict)'
}

GhcMachineOrthography = build_orthography_class(GhcVector, ghc_machine_orthography)

# Explicitly define the phonology and its associated orthographies
Ghc = {
    'phonology': GhcVector,
    'orthographies': {
        'standard': GhcOrthography,
        'machine': GhcMachineOrthography
    }
}

# Example usage
if __name__ == "__main__":
    # Create a syllable from a string
    syllable = GhcOrthography("lhja²")
    print(f"Parsed syllable: {syllable}")
    
    # Access phonological features
    print(f"Initial: {syllable['声母']}")
    print(f"Rhyme class: {syllable['摄']}")
    print(f"Tone: {syllable['声调']}")
    
    # Parse multiple syllables
    text = "lhja² khwə¹"
    syllables = GhcOrthography.parse_all(text)
    print(f"Parsed text '{text}':")
    for syl in syllables:
        print(f"  {syl}") 