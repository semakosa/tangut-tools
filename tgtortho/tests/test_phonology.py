"""
Tests for the phonology module.
"""

import unittest
from collections import namedtuple

from tgtortho.phonology import PhonologicalVector, build_phonological_vector_class, build_orthography_class


class TestPhonologicalVector(unittest.TestCase):
    """Tests for the PhonologicalVector class."""

    def setUp(self):
        """Set up the test fixture."""
        # Create a test specification
        self.spec = {
            'reconstruction_id': 'test',
            'specification': {
                'feature1': ['a', 'b', 'c'],
                'feature2': ['1', '2', '3'],
                'feature3': ['+', '-'],
            }
        }
        # Create a test class
        self.TestVector = build_phonological_vector_class(self.spec)
        # Create a test namedtuple
        self.test_tuple = self.TestVector.namedtuple_type(feature1='a', feature2='1', feature3='+')
        # Create a test vector
        self.vector = self.TestVector(self.test_tuple)

    def test_init(self):
        """Test initialization."""
        # Test initialization with a namedtuple
        vector = self.TestVector(self.test_tuple)
        self.assertEqual(vector['feature1'], 'a')
        self.assertEqual(vector['feature2'], '1')
        self.assertEqual(vector['feature3'], '+')

        # Test initialization with an invalid namedtuple
        Tuple2 = namedtuple('Tuple2', ['other_feature'])
        with self.assertRaises(TypeError):
            self.TestVector(Tuple2(other_feature='value'))

        # Test initialization with invalid values
        with self.assertRaises(ValueError):
            self.TestVector(self.TestVector.namedtuple_type(feature1='invalid', feature2='1', feature3='+'))

    def test_getitem(self):
        """Test __getitem__."""
        self.assertEqual(self.vector['feature1'], 'a')
        self.assertEqual(self.vector['feature2'], '1')
        self.assertEqual(self.vector['feature3'], '+')

    def test_setitem(self):
        """Test __setitem__."""
        # Test valid value
        self.vector['feature1'] = 'b'
        self.assertEqual(self.vector['feature1'], 'b')

        # Test invalid value
        with self.assertRaises(ValueError):
            self.vector['feature1'] = 'invalid'

        # Test invalid key
        with self.assertRaises(ValueError):
            self.vector['invalid'] = 'value'

    def test_len(self):
        """Test __len__."""
        self.assertEqual(len(self.vector), 3)

    def test_iter(self):
        """Test __iter__."""
        keys = list(self.vector)
        self.assertEqual(set(keys), {'feature1', 'feature2', 'feature3'})

    def test_contains(self):
        """Test __contains__."""
        self.assertIn('feature1', self.vector)
        self.assertNotIn('invalid', self.vector)

    def test_keys(self):
        """Test keys()."""
        self.assertEqual(set(self.vector.keys()), {'feature1', 'feature2', 'feature3'})

    def test_values(self):
        """Test values()."""
        values = list(self.vector.values())
        self.assertIn('a', values)
        self.assertIn('1', values)
        self.assertIn('+', values)

    def test_items(self):
        """Test items()."""
        items = dict(self.vector.items())
        self.assertEqual(items['feature1'], 'a')
        self.assertEqual(items['feature2'], '1')
        self.assertEqual(items['feature3'], '+')

    def test_get(self):
        """Test get()."""
        self.assertEqual(self.vector.get('feature1'), 'a')
        self.assertEqual(self.vector.get('invalid'), None)
        self.assertEqual(self.vector.get('invalid', 'default'), 'default')

    def test_eq(self):
        """Test __eq__."""
        # Test equal vectors
        vector2 = self.TestVector(self.test_tuple)
        self.assertEqual(self.vector, vector2)

        # Test unequal vectors
        test_tuple2 = self.TestVector.namedtuple_type(feature1='b', feature2='1', feature3='+')
        vector3 = self.TestVector(test_tuple2)
        self.assertNotEqual(self.vector, vector3)

    def test_update(self):
        """Test update()."""
        # Test valid update
        self.vector.update(feature1='b', feature2='2')
        self.assertEqual(self.vector['feature1'], 'b')
        self.assertEqual(self.vector['feature2'], '2')

        # Test invalid update
        with self.assertRaises(ValueError):
            self.vector.update(feature1='invalid')


class TestOrthography(unittest.TestCase):
    """Tests for the Orthography class built by build_orthography_class."""

    def setUp(self):
        """Set up the test fixture."""
        # Create a test specification
        self.spec = {
            'reconstruction_id': 'test',
            'specification': {
                'feature1': ['a', 'b', 'c'],
                'feature2': ['1', '2', '3'],
                'feature3': ['+', '-'],
            }
        }
        # Create a test vector class
        self.TestVector = build_phonological_vector_class(self.spec)
        
        # Create a simple orthography specification
        self.ortho_spec = {
            'fst': {
                "Feature1": {
                    "union": ["a", "b", "c"]
                },
                "Feature2": {
                    "union": ["1", "2", "3"]
                },
                "Feature3": {
                    "union": ["+", "-"]
                },
                "Syllable": {
                    "concat": ["Feature1", "*", "Feature2", "*", "Feature3"]
                }
            },
            'substitutions': [],
            'keys': ['feature1', 'feature2', 'feature3'],
            'parse': 'Syllable',
            'generate': 'Syllable'
        }
        
        # Create a test orthography class
        self.TestOrtho = build_orthography_class(self.TestVector, self.ortho_spec)

    def test_init_from_string(self):
        """Test initialization from a string."""
        ortho = self.TestOrtho("a1+")
        self.assertEqual(ortho['feature1'], 'a')
        self.assertEqual(ortho['feature2'], '1')
        self.assertEqual(ortho['feature3'], '+')

    def test_init_from_vector(self):
        """Test initialization from a vector."""
        vector = self.TestVector(self.TestVector.namedtuple_type(feature1='a', feature2='1', feature3='+'))
        ortho = self.TestOrtho(vector)
        self.assertEqual(ortho['feature1'], 'a')
        self.assertEqual(ortho['feature2'], '1')
        self.assertEqual(ortho['feature3'], '+')

    def test_str(self):
        """Test string generation."""
        vector = self.TestVector(self.TestVector.namedtuple_type(feature1='a', feature2='1', feature3='+'))
        ortho = self.TestOrtho(vector)
        self.assertEqual(str(ortho), 'a1+')

    def test_parse_all(self):
        """Test parse_all method."""
        orthos = self.TestOrtho.parse_all("a1+ b2-")
        self.assertEqual(len(orthos), 2)
        self.assertEqual(str(orthos[0]), 'a1+')
        self.assertEqual(str(orthos[1]), 'b2-')


if __name__ == '__main__':
    unittest.main() 