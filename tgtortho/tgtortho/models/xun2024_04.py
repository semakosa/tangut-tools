"""
Xun Gong reconstruction, version April 2024.

This module provides classes for working with Xun Gong's April 2024 
reconstruction of Tangut phonology.
"""

from tgtortho.phonology import build_phonological_vector_class, build_orthography_class

# Xun Gong reconstruction, version April 2024
gx202404_specification = {
    'reconstruction_id': "gx202404",
    'specification': {
        '卷舌冠音': ['-', '+'],
        '鼻冠音': ['-', '+'],
        '声母': [
            'p', 'ph', 'b', 'm', 
            'v', 'f',
            't', 'th', 'd', 'n', 
            'ṇ',
            'ts', 'tsh', 'dz', 's', 'z', 
            'tś', 'tśh', 'dź', 'ś', 'ź',
            'k', 'kh', 'g', 'ŋ',       
            'h', 'γ', 'y', 'ʔ',
            'r', 'l', 'lh',], 
        '合口': ['-', '+'],
        '元音': ['a', 'i', 'u', 'e', 'o', 'ə', 'uo'], 
        '韵尾': ['', 'w', 'N'],
        '卷舌': ['-', '+'],
        '紧': ['-', '+'],
        '等': ['1', '2', '3'],
        '声调': ['平', '上']
    }
}

GX202404Vector = build_phonological_vector_class(gx202404_specification)

gx202404_orthography = {
    'fst': {
        "RetroflexPreinitial": {
            "union": [":-", "R:+"]
        },
        "InvariantInitial": {
            "union": ["p", "t", "ts",
                      "ph", "th", "tsh",
                      "b", "d", "dz",
                      "m", "n",
                      "ṇ",
                      "s",
                      "h", "γ",
                      "z", "r", "l", "lh",
                      ':ʔ', "v"]
        },
        "InvariantInitialWithNasal": {
            "union": ["mp:p", "nt:t", "nts:ts",
                      "mph:ph", "nth:th", "ntsh:tsh",
                      "mb:b", "nd:d", "ndz:dz",
                      "mm:m", "nn:n",
                      "ns:s",
                      "nh:h", "nγ:γ",
                      "nz:z", "nl:l",
                      "nr:r", "nlh:lh", 
                      "nv:v"]
        },
        "UvularInitial": {
            "union": ["InvariantInitial",
                    "q:k", "qh:kh", "ġ:g", "ŋ:ŋ",
                    "tṣ:tś", "tṣh:tśh", "dẓ:dź", "ṣ:ś", "ẓ:ź",
                    ]
        },
        "UvularInitialWithNasal": {
            "union": ["InvariantInitialWithNasal",
                    "ŋq:k", "ŋqh:kh", "ŋġ:g", "ŋŋ:ŋ",
                    "ntṣ:tś", "ntṣh:tśh", "ndẓ:dź", "nṣ:ś", "nẓ:ź"]
        },
        "VelarInitial": {
            "union": ["InvariantInitial",
                    "k", "kh", "g", "ŋ",
                    "tś", "tśh", "dź", "ś", "ź",
                    "y", "f"]
        },
        "VelarInitialWithNasal": {
            "union": ["InvariantInitialWithNasal",
                    "ŋk:k", "ŋkh:kh", "ŋg:g", "ŋŋ:ŋ",
                    "ntś:tś", "ntśh:tśh", "ndź:dź", "nś:ś", "nź:ź",
                    "n·y:y"]
        },
        "PreinitialUvularInitial": {
            "union": [
                {"concat": [':-', '*', 'UvularInitial']},
                {"concat": [':+', '*', 'UvularInitialWithNasal']}]},
        "PreinitialVelarInitial": {
            "union": [
                {"concat": [':-', '*', 'VelarInitial']},
                {"concat": [':+', '*', 'VelarInitialWithNasal']}]},
        "Rounding": {
            "union": [":-", "w:+"]
        },
        "Vowel": {
            "union": ["i", "e", "ə", "u", "a", "o"]
        },
        "VelarVowel": {
            "union": ["i", "e", "ə", "u", "a", "o", "uo"]
        },
        "InitialGradeAndVowel": {
            "union": [
                {"concat": ["PreinitialUvularInitial", "*", "Rounding", "*", ":1", "*", "Vowel", "_:"]},
                {"concat": ["PreinitialUvularInitial", "*", "Rounding", "*", "a:2", "*", "Vowel", "_:"]},
                {"concat": ["PreinitialVelarInitial", "*", "Rounding", "*", ":3", "*", "VelarVowel"]}
            ]
        },
        "Tenseness": {
            "union": [":-", "h:+"]
        },
        "Retroflex": {
            "union": [":-", "r:+"]
        },
        "Coda": {
            "union": ["", "N", "w"]
        },
        "Tone": {
            "union": ["1:平", "2:上"]
        },
        "Syllable": {
            "concat": ["RetroflexPreinitial", "*", "InitialGradeAndVowel", "*", "Coda", "*", 'Retroflex', "*",'Tenseness', '*',  "Tone"]
        },
    },
    'substitutions': [
        ('Rr', 'r'),
        ('R', 'r'),
        ('_', "̱"),
        ('_', '̠'),
        ("N", "ṁ"),
        ('1', "¹"),
        ('2', "²"),
    ],
    'substitutions_parse': [
        ('Rr', 'R[aeiouəw]'),
        ('R', '^r'),
        ('_', "̱"),
        ('_', '̠'),
        ("N", "ṁ"),
        ('1', "¹"),
        ('2', "²"),
    ],
    'keys': ['卷舌冠音', '鼻冠音', '声母', '合口', '等', '元音', '韵尾', '卷舌', '紧', '声调'],
    'parse': 'Syllable',
    'generate': 'Syllable'
}

GX202404Orthography = build_orthography_class(GX202404Vector, gx202404_orthography)

# Xun Gong reconstruction, alternative orthography
gx202404_ipa = {
    'fst': {
        "RetroflexPreinitial": {
            "union": [":-", "R:+"]
        },
        "InvariantInitial": {
            "union": ["p", "t", "ts",
                        "pʰ:ph", "tʰ:th", "tsʰ:tsh",
                        "b", "d", "dz",
                        "m", "n",
                        "ɳʵ:ṇ",
                        "s",
                        "z", "ɻ:r", "l", "ɬ:lh",
                        'ʔ']
        },
        "InvariantInitialWithNasal": {
            "union": ["mp:p", "nt:t", "nts:ts",
                        "mpʰ:ph", "ntʰ:th", "ntsʰ:tsh",
                        "mb:b", "nd:d", "ndz:dz",
                        "mm:m", "nn:n",
                        "n̚s:s",
                        "n̚z:z",
                        "n̚ɻ:r", "nl:l", "nɬ:lh"]
        },
        "UvularInitial": {
            "union": ["InvariantInitial",
                      "w:v",
                      "q:k", "qʰ:kh", "ɢ:g", "ɴ:ŋ",
                      "tʂ:tś", "tʂh:tśh", "dʐ:dź", "ʂ:ś", "ʐ:ź",
                      "χ:h", "ʁ:γ"]
        },
        "UvularInitialWithNasal": {
            "union": ["InvariantInitialWithNasal",
                      "n̚w:v",
                      "ɴq:k", "ɴqʰ:kh", "ɴɢ:g", "ɴɴ:ŋ",
                      "ntʂ:tś", "ntʂʰ:tśh", "ndʐ:dź", "n̚ʂ:ś", "n̚ʐ:ź",
                      ]
        },
        "VelarInitial": {
            "union": ["InvariantInitial",
                      "ʋ:v",
                      "k", "kʰ:kh", "ɡ:g",
                      "tɕ:tś", "tɕʰ:tśh", "dʑ:dź", "ɕ:ś", "ʑ:ź",
                      "x:h", "ɣ:γ",
                      "j:y", "f"]
        },
        "VelarInitialWithNasal": {
            "union": ["InvariantInitialWithNasal",
                      "n̚ʋ:v",
                      "ŋk:k", "ŋkʰ:kh", "ŋɡ:g", "ŋŋ:ŋ",
                     "ntɕ:tś", "ntɕʰ:tśh", "ndʑ:dź", "n̚ɕ:ś", "n̚ʑ:ź",
                      "n̚ʝ:y"]
        },
        "PreinitialUvularInitial": {
            "union": [
                {"concat": [':-', '*', 'UvularInitial']},
                {"concat": [':+', '*', 'UvularInitialWithNasal']}]},
        "PreinitialVelarInitial": {
            "union": [
                {"concat": [':-', '*', 'VelarInitial']},
                {"concat": [':+', '*', 'VelarInitialWithNasal']}]},
        "Rounding": {
            "union": [":-", "w:+"]
        },
        "GradeAndVowel1": {"union": ["Gɪʶ:i", "Gɛʶ:e", "ʌʶ:ə", "ʊʶ:u", "ɑʶ:a", "ɔʶ:o"]},
        "GradeAndVowel2": {"union": ["ˤæˤ:a", "ˤæ̯ɛ:e", "ˤəˤ:ə", "ˤə̯ɪ:i", "ˤɞ̯ɔ:o", "ˤɵ̯ʊ:u"]},
        "GradeAndVowel3": {"union": ["ɐ:a", "Ye:e", "ɨ:ə", "Yi:i", "ɵ:o", "ʉ:u", "ʉ͡ɵ:uo"]},
        "InitialGradeAndVowel": {
            "union": [
                {"concat": ["PreinitialUvularInitial", "*", ":1", "*", "Rounding", "*", "GradeAndVowel1"]},
                {"concat": ["PreinitialUvularInitial", "*", ":2", "*", "Rounding", "*", "GradeAndVowel2"]},
                {"concat": ["PreinitialVelarInitial", "*", ":3", "*", "Rounding", "*", "GradeAndVowel3"]}
            ]        
        },
        "Tenseness": {
            "union": [":-", "!:+"]
        },
        "Retroflex": {
            "union": [":-", "ṛ:+"]
        },
        "Coda": {
            "union": ["", "w̃:N", "ɰ:w"]
        },
        "Tone": {
            "union": [
                {"concat": ["˥˨:平", "*", ":-"]},
                {"concat": ["˧˧˦:上", "*", ":-"]},
                {"concat": ["˥˧ˀ:平", "*", ":+"]},
                {"concat": ["˧ˀ:上", "*", ":+"]}
            ],
        },
        "Syllable": {
            "concat": ["RetroflexPreinitial", "*", "InitialGradeAndVowel", "*", 'Tenseness', '*', 'Retroflex', "*", "Coda", "*", "Tone"]
        },
    },
    'substitutions': [
        ('wɰ', 'w'),
        # 韻尾使得前元音變成後元音
        ('ɵɰ', 'ow'),
        ('iɰ', 'ɪɰ'),
        ('Gɪʶɰ', 'əʶɰ'),
        ('ˤə̯ɪɰ', 'əˤɰ'),
        # Preserve initial R before yod and harden the yod
        ('Rj', 'ɻʝ'),
        # Velarization and palatalization
        ('lG', 'ɫ'),
        ('ʋY', 'ʋʲ'),
        # remove placeholders
        ('R', ''),
        ('G', ''),
        ('Y', ''),
        # fix tenseness and retroflex position
        ("ʶ!", "!ʶ"),
        ("ʶṛ", "ṛʶ"),
        # switch to diacritics
        ("!", "̰"),
        ("ṛ", "˞"),
    ],
    'keys': ['卷舌冠音', '鼻冠音', '声母', '等', '合口', '元音', '紧', '卷舌', '韵尾', '声调', '紧'],
    'parse': 'Syllable',
    'generate': 'Syllable'
}

GX202404IPA = build_orthography_class(GX202404Vector, gx202404_ipa)

# Explicitly define the phonology and its associated orthographies
GX202404 = {
    'phonology': GX202404Vector,
    'orthographies': {
        'standard': GX202404Orthography,
        'ipa': GX202404IPA
    }
}

# Example usage
if __name__ == "__main__":
    # Create a syllable from a string
    syllable = GX202404Orthography("tśhə¹")
    print(f"Parsed syllable: {syllable}")
    
    # Access phonological features
    print(f"Initial: {syllable['声母']}")
    print(f"Vowel: {syllable['元音']}")
    print(f"Tone: {syllable['声调']}")
    
    # Parse multiple syllables
    text = "tśhə¹ kha²"
    syllables = GX202404Orthography.parse_all(text)
    print(f"Parsed text '{text}':")
    for syl in syllables:
        print(f"  {syl}") 