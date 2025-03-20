#!/usr/bin/env python3
"""
Test script for FST validation functionality.

This script demonstrates how to use the FST validation features in the orthography module
by testing the GX202411 model as an example. It shows how to:

1. Enable debug mode to see detailed logging of the FST structure
2. Retrieve and analyze the FST structure
3. Generate a visual representation of the FST
4. Test parsing and generation with sample text
5. Display the feature breakdown for parsed syllables

The FST validation checks for:
- Consistency of separator counts across branches in union definitions
- Proper mapping of features to FST variables based on their positions
- Correct structure of entry points for parsing and generation
"""

import logging
from tgtortho.models.xun2024_11 import GX202411Orthography

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """
    Test the FST validation functionality.
    
    This function demonstrates how to use the FST validation features
    by working with the GX202411Orthography model.
    """
    logger.info("Testing FST validation with GX202411Orthography")
    
    # Enable debug mode to see detailed logging
    GX202411Orthography.set_debug_mode(True)
    
    # Get FST structure analysis
    logger.info("Retrieving FST structure analysis")
    fst_analysis = GX202411Orthography.debug_fst_structure()
    
    # Print visualization
    logger.info("Generating FST structure visualization")
    visualization = GX202411Orthography.visualize_fst_structure()
    print("\n" + visualization)

    # Test parsing and generation
    test_text = "tśhə¹ kha²"
    logger.info(f"Testing parsing with text: '{test_text}'")
    
    # Parse the text
    syllables = GX202411Orthography.parse_all(test_text)
    logger.info(f"Successfully parsed {len(syllables)} syllables")
    
    # Display results
    for i, syl in enumerate(syllables):
        logger.info(f"Syllable {i+1}: {syl}")
        # Generate the string representation
        output = str(syl)
        logger.info(f"Generated: {output}")
        
        # Show feature breakdown
        features = syl.debug_features()
        for key, value in features.items():
            logger.info(f"  {key}: {value}")

if __name__ == "__main__":
    main() 