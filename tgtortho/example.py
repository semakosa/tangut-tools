#!/usr/bin/env python3
"""
Example usage of the tgtortho package.

This file demonstrates the core functionality of the tgtortho package,
including parsing, feature access, modification, and debugging capabilities.
"""

import logging
from tgtortho.models import GX202411Orthography

def main():
    print("TgtOrtho - Tangut Orthography Library Example")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: %(message)s'
    )
    
    # Basic usage without debugging
    print("\n1. BASIC USAGE")
    print("-" * 50)
    
    # Parse a single syllable
    print("\nParsing a single syllable:")
    syllable = GX202411Orthography("tśhə¹")
    print(f"Parsed: {syllable}")
    
    # Access phonological features
    print("\nAccessing phonological features:")
    print(f"Initial: {syllable['声母']}")
    print(f"Vowel: {syllable['元音']}")
    print(f"Tone: {syllable['声调']}")
    
    # Modify features
    print("\nModifying features:")
    original = str(syllable)
    syllable['声调'] = '上'
    print(f"Changed tone: {original} -> {syllable}")
    
    syllable['元音'] = 'a'
    print(f"Changed vowel: {original} -> {syllable}")
    
    syllable['合口'] = '+'
    print(f"Added labialization: {original} -> {syllable}")
    
    # Parse multiple syllables
    print("\nParsing multiple syllables:")
    text = "tśhə¹ kha² lo¹ ma²"
    syllables = GX202411Orthography.parse_all(text)
    print(f"Input: {text}")
    print("Parsed syllables:")
    for i, syl in enumerate(syllables, 1):
        features = ", ".join([f"{k}: {v}" for k, v in syl.items() if k in ['声母', '元音', '韵尾', '声调']])
        print(f"  {i}. {syl} ({features})")
    
    # DEBUGGING FUNCTIONALITY
    print("\n2. DEBUGGING FUNCTIONALITY")
    print("-" * 50)
    
    # Enable class-level debugging
    print("\nEnabling class-level debugging:")
    GX202411Orthography.set_debug_mode(True)
    
    print("\nParsing with debugging enabled:")
    debug_syllable = GX202411Orthography("tśhə¹")
    print(f"Parsed with debugging: {debug_syllable}")
    
    # Display detailed feature information
    print("\nDetailed feature breakdown:")
    debug_syllable.debug_features()
    
    # Parse a complex example with debug info
    print("\nParsing a complex syllable with debugging:")
    complex_syllable = GX202411Orthography("Rdzwəw²")
    print(f"Complex syllable parsed: {complex_syllable}")
    
    # Disable class-level debugging and use instance-level debugging
    print("\nDisabling class-level debugging:")
    GX202411Orthography.set_debug_mode(False)
    
    # Instance-level debugging
    print("\nInstance-level debugging:")
    instance_debug = GX202411Orthography("kha²", debug=True)
    print(f"Instance-level debug syllable: {instance_debug}")
    
    # Step-by-step debugging of parse_all
    print("\nStep-by-step debugging of parse_all:")
    debug_syllables = GX202411Orthography.parse_all("tśhə¹ kha² invalid ma²", debug=True)
    print(f"Parsed {len(debug_syllables)} valid syllables")
    
    print("\nCombining debug with feature modification:")
    debug_syllable = GX202411Orthography("tśhə¹", debug=True)
    original = str(debug_syllable)
    debug_syllable['声母'] = 'p'
    print(f"Modified initial: {original} -> {debug_syllable}")

if __name__ == "__main__":
    main() 