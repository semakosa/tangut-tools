"""Tests for the GHC (Gong-Hwang-Coblin) model."""

import unittest
from tgtortho.models import GhcVector, GhcOrthography, ghc_specification


class TestGhcModel(unittest.TestCase):
    """Tests for the GHC model structure and functionality."""
    
    def test_specification_structure(self):
        """Test that the specification has the expected structure."""
        self.assertIn('reconstruction_id', ghc_specification)
        self.assertIn('specification', ghc_specification)
        self.assertEqual(ghc_specification['reconstruction_id'], 'ghc')
        
        # Check that all required features are present
        expected_features = ['声母', '合口', '摄', '卷舌', '紧', '长', '等', '声调']
        for feature in expected_features:
            self.assertIn(feature, ghc_specification['specification'])
            self.assertIsInstance(ghc_specification['specification'][feature], list)
            self.assertTrue(len(ghc_specification['specification'][feature]) > 0)
    
    def test_vector_class(self):
        """Test that the vector class is properly configured."""
        # Check class properties
        self.assertEqual(GhcVector.reconstruction_id, 'ghc')
        
        # Check that all expected features are in the specification
        for feature in ['声母', '合口', '摄', '卷舌', '紧', '长', '等', '声调']:
            self.assertIn(feature, GhcVector.specification)
        
        # Check creating a vector from a dictionary
        vector = GhcVector({
            '声母': 'p',
            '合口': '-',
            '摄': 'a',
            '卷舌': '-',
            '紧': '-',
            '长': '-',
            '等': '1',
            '声调': '平'
        })
        
        # Access each property to check that it works
        for feature in ['声母', '合口', '摄', '卷舌', '紧', '长', '等', '声调']:
            self.assertIsNotNone(vector[feature])
    
    def test_parse_basic(self):
        """Test basic parsing functionality."""
        try:
            syl = GhcOrthography("lhja²")
            self.assertEqual(syl['声母'], 'lh')
            self.assertEqual(syl['摄'], 'a')
            self.assertEqual(syl['声调'], '上')
            
            syl = GhcOrthography("khwə¹")
            self.assertEqual(syl['声母'], 'kh')
            self.assertEqual(syl['合口'], '+')
            self.assertEqual(syl['摄'], 'ə')
            self.assertEqual(syl['声调'], '平')
        except Exception as e:
            self.fail(f"Parsing failed with exception: {e}")
    
    def test_generate(self):
        """Test generation from feature vectors."""
        try:
            # Parse a known syllable first, then use it for generation
            syl = GhcOrthography("lhja²")
            self.assertEqual(str(syl), "lhja²")
            
            # Create a new syllable from an existing one
            syl['声调'] = '平'
            self.assertEqual(str(syl), "lhja¹")
        except Exception as e:
            self.fail(f"Vector generation failed with exception: {e}")
    
    def test_dropdown_indexes(self):
        """Test that all dropdown indexes would be in range."""
        # Create a base syllable to modify for testing
        try:
            base_syllable = GhcOrthography("lhja²")
            
            # Test modifying each feature
            for feature, values in ghc_specification['specification'].items():
                if feature == 'reconstruction_id':
                    continue
                
                # Try each possible value for this feature
                for value in values:
                    try:
                        # Create a copy by parsing again
                        test_syllable = GhcOrthography("lhja²")
                        # Try to set the value
                        test_syllable[feature] = value
                        # Verify the value was set
                        self.assertEqual(test_syllable[feature], value)
                    except Exception as e:
                        self.fail(f"Testing {feature}={value} failed with: {e}")
        except Exception as e:
            self.fail(f"Base test setup failed with: {e}")


if __name__ == '__main__':
    unittest.main()
