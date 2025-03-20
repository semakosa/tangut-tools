#!/usr/bin/env python3
"""
Debug script for the GHC model.
"""

import inspect
from collections import namedtuple
from tgtortho.models import GhcVector, GhcOrthography, ghc_specification

def debug_ghc_model():
    """Debug the GHC model."""
    print("=== GHC Model Debug ===")
    
    print("\n1. Checking GHC specification structure:")
    print(f"reconstruction_id: {ghc_specification['reconstruction_id']}")
    print("Features in specification:")
    for key, values in ghc_specification['specification'].items():
        print(f"  {key}: {values}")
    
    print("\n2. Checking GhcVector class attributes:")
    print(f"GhcVector.reconstruction_id: {GhcVector.reconstruction_id}")
    print(f"GhcVector.namedtuple_type: {GhcVector.namedtuple_type}")
    print("GhcVector.specification:")
    for key, values in GhcVector.specification.items():
        print(f"  {key}: {values}")
    
    print("\n3. Testing namedtuple creation:")
    try:
        field_names = GhcVector.namedtuple_type._fields
        print(f"Namedtuple fields: {field_names}")
        
        # Create dictionary with default values
        default_values = {}
        for field in field_names:
            default_values[field] = GhcVector.specification[field][0]
        
        print(f"Default values: {default_values}")
        
        # Create a namedtuple instance
        nt = GhcVector.namedtuple_type(**default_values)
        print(f"Created namedtuple: {nt}")
        
        # Create a vector
        vector = GhcVector(nt)
        print(f"Created vector: {vector}")
        
    except Exception as e:
        print(f"Error creating namedtuple: {e}")
    
    print("\n4. Simulating tangut_explorer dropdown behavior:")
    try:
        # Get selected values from dropdowns (simulating the UI)
        values = {}
        for feature, feature_values in GhcVector.specification.items():
            # In the explorer, it uses dropdown.get_selected() which returns an index
            # Then it does: values[feature] = feature_values[selected_idx]
            selected_idx = 0  # We start with the first item in each dropdown
            
            # This would be the line causing the error if feature_values doesn't match what's indexed
            print(f"Feature: {feature}, Selected idx: {selected_idx}")
            try:
                selected_value = feature_values[selected_idx]
                print(f"  Selected value: {selected_value}")
                values[feature] = selected_value
            except IndexError:
                print(f"  ERROR: Index {selected_idx} out of range for feature {feature} with values {feature_values}")
        
        print(f"Collected values: {values}")
        
        # Create a namedtuple from the values
        nt = GhcVector.namedtuple_type(**values)
        vector = GhcVector(nt)
        orthography = GhcOrthography(vector)
        print(f"Result string: {str(orthography)}")
        
    except Exception as e:
        print(f"Explorer simulation error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n5. Testing parsing:")
    try:
        # Try parsing a valid GHC syllable
        syl = GhcOrthography("lhja²")
        print(f"Parsed syllable: {syl}")
        print(f"Features: {dict(syl.items())}")
    except Exception as e:
        print(f"Parsing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ghc_model() 