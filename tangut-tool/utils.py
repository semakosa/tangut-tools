import csv
import os
from collections import namedtuple

class GlossingModel:
    """
    Model for managing Tangut glossing data.
    
    This model stores words, their relationships to one another, and their glosses.
    It handles the logic for updating relationships and glosses, as well as
    transforming the data for display.
    """
    
    def __init__(self, words, relationships, glosses):
        """
        Initialize the glossing model.
        
        Args:
            words: List of Tangut words/characters
            relationships: List of relationship indicators between words (' ', '-', '.')
            glosses: List of glosses for each word
        """
        self.words = words.copy()
        self.relationships = relationships.copy()
        self.glosses = glosses.copy()

    def update_relationship(self, index, new_relation):
        """
        Update the relationship at the specified index.
        
        Args:
            index: The index of the relationship to update
            new_relation: The new relationship value (' ', '-', or '.')
        """
        if 0 <= index < len(self.relationships):
            old_relation = self.relationships[index]
            self.relationships[index] = new_relation
            transformed_index = self.find_transformed_index(index)

            if new_relation == "." and old_relation != ".": 
                self.merge_glosses(transformed_index)
            elif new_relation != "." and old_relation == ".":
                self.split_glosses(transformed_index)

    def merge_glosses(self, index):
        """
        Merge glosses when a dot relationship is established.
        
        If both glosses have content, they are joined with a dot.
        If either is empty, we use the non-empty one.
        
        Args:
            index: The index of the first gloss to merge
        """
        if 0 <= index < len(self.glosses) - 1:
            first_gloss = self.glosses[index]
            second_gloss = self.glosses[index + 1]
            
            # If both have content, join them with a dot
            if first_gloss and second_gloss:
                merged_gloss = first_gloss + '.' + second_gloss
            # If only one has content, use that one
            elif first_gloss:
                merged_gloss = first_gloss
            elif second_gloss:
                merged_gloss = second_gloss
            # If both are empty, leave empty
            else:
                merged_gloss = ""
                
            self.glosses[index] = merged_gloss
            del self.glosses[index + 1]

    def split_glosses(self, index):
        """
        Split the glosses when a dot relationship is removed.
        
        This creates a new empty gloss for the second word.
        If the gloss contains a dot, we'll try to split it intelligently.
        
        Args:
            index: The index of the gloss to split
        """
        if 0 <= index < len(self.glosses):
            current_gloss = self.glosses[index]
            
            # Try to split the gloss at a dot if it exists
            if '.' in current_gloss:
                parts = current_gloss.split('.')
                if len(parts) >= 2:
                    self.glosses[index] = parts[0]
                    self.glosses.insert(index + 1, parts[1])
                    return
            
            # If we couldn't split intelligently, just insert an empty gloss
            self.glosses.insert(index + 1, "")

    def update_gloss(self, index, new_gloss):
        """
        Update the gloss at the specified index.
        
        Args:
            index: The index of the gloss to update
            new_gloss: The new gloss text
        """
        if 0 <= index < len(self.glosses):
            self.glosses[index] = new_gloss

    def find_transformed_index(self, original_index):
        """
        Convert an index in the original data to an index in the transformed data.
        
        Args:
            original_index: The index in the original data
            
        Returns:
            The corresponding index in the transformed data
        """
        transformed_index = 0
        i = 0
        while i < original_index:
            if i < len(self.relationships) and self.relationships[i] == ".":
                # Skip over the grouped words
                while i < len(self.relationships) and self.relationships[i] == ".":
                    i += 1
            else:
                i += 1
                transformed_index += 1

        return transformed_index

    def get_current_state(self):
        """
        Get the current state of the model.
        
        Returns:
            A tuple of (words, relationships, glosses)
        """
        return self.words, self.relationships, self.glosses

    def get_transformed_data(self):
        """
        Transform the data for display, grouping words based on relationships.
        
        Returns:
            A tuple of (transformed_words, transformed_relationships)
        """
        words, relationships = self.words, self.relationships
        transformed_words, transformed_relationships = [], []
    
        i = 0
        while i < len(words):
            if i < len(relationships) and relationships[i] == ".":
                # Group words with "." relationship
                group = [words[i]]
                while i < len(relationships) and relationships[i] == ".":
                    i += 1
                    group.append(words[i])
                transformed_words.append(group)
                if i < len(relationships):
                    transformed_relationships.append(relationships[i])
            else:
                transformed_words.append([words[i]])
                if i < len(relationships):
                    transformed_relationships.append(relationships[i])
            i += 1
    
        return transformed_words, transformed_relationships


class DataLoader:
    """
    Loads and manages Tangut character data from local TSV files.
    
    This class provides access to pronunciation and glossary data for Tangut characters.
    """
    
    def __init__(self):
        """
        Initialize the data loader and load data from TSV files.
        """
        self.pronunciations = {}
        self.glossary = {}
        self.unicode_to_li = {}
        self.li_to_unicode = {}
        self.load_data()
        
    def load_data(self):
        """Load all necessary data from TSV files."""
        # Load pronunciation data from TSV
        self._load_pronunciation_data()
        # Load glossary data from TSV
        self._load_glossary_data()
        
    def _load_pronunciation_data(self):
        """Load pronunciation data from the TSV file."""
        pronunciation_file = os.path.join('data', '20241129.tsv')
        try:
            with open(pronunciation_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    unicode_char = row['unicode']
                    li = row.get('li', '')  # Make li optional
                    
                    # Store data with unicode as primary key
                    self.pronunciations[unicode_char] = row
                    
                    # Still maintain the li mappings if available
                    if li:
                        self.unicode_to_li[unicode_char] = li
                        self.li_to_unicode[li] = unicode_char
        except Exception as e:
            print(f"Error loading pronunciation data: {e}")
            
    def _load_glossary_data(self):
        """Load glossary data from the TSV file."""
        glossary_file = os.path.join('data', 'glossary.tsv')
        try:
            with open(glossary_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                for row in reader:
                    unicode_char = row['unicode']
                    meanings = row['meanings'].split(',')
                    self.glossary[unicode_char] = {
                        'unicode': unicode_char,
                        'meanings': meanings
                    }
        except Exception as e:
            print(f"Error loading glossary data: {e}")


# Global data loader instance
data_loader = DataLoader()


# Utility functions
def superscriptize(s):
    """
    Convert numbers to superscript in a string.
    
    Args:
        s: The string to convert
        
    Returns:
        The string with numbers converted to superscript
    """
    tr2 = str.maketrans('012?', '⁰¹²﹖')
    return s.translate(tr2)


def clean_english_gloss(s):
    """
    Clean up an English gloss by removing common prefixes.
    
    Args:
        s: The gloss to clean
        
    Returns:
        The cleaned gloss
    """
    prefixes = ['a ', 'the ', 'an ', 'to ']
    s = s.strip()
    for pfx in prefixes:
        if s.startswith(pfx):
            s = s[len(pfx):]
    return s


# Named tuple for storing Tangut character data
TangutData = namedtuple('TangutData', ['unicode', 'li', 'reconstruction', 'semantics'])


def fetch_data(ch, reconstruction_choice='GX202411'):
    """
    Fetch data for a Tangut character using local data files.
    
    Args:
        ch: The Tangut Unicode character
        reconstruction_choice: The pronunciation reconstruction system to use
        
    Returns:
        A TangutData namedtuple with character information
    """
    li = '?'
    semantics = []
    phonology = '?'
    
    # Get the Li code from Unicode if available
    if ch in data_loader.unicode_to_li:
        li = data_loader.unicode_to_li[ch]
    
    # Get pronunciation data directly using Unicode
    if ch in data_loader.pronunciations:
        pronunciation_data = data_loader.pronunciations[ch]
        if reconstruction_choice in pronunciation_data and pronunciation_data[reconstruction_choice]:
            phonology = pronunciation_data[reconstruction_choice]
        else:
            phonology = '?'
    
    # Get meaning data
    if ch in data_loader.glossary:
        semantics = data_loader.glossary[ch]['meanings']
    
    # If we have no meanings but have a character, provide a placeholder
    if not semantics and ch:
        semantics = ['?']
    
    semantics = [s.replace(' ', '.') for s in semantics]
    
    return TangutData(ch, li, phonology, semantics)
