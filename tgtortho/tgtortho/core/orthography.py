"""
Orthography module.

This module provides functions for building orthography classes based on
phonological vector classes and parser specifications, with debugging capabilities.
"""

import re
import logging
from .fst import translate_minilanguage, fst_down, fst_up

# Configure logger
logger = logging.getLogger(__name__)

def build_orthography_class(base_class, parser_spec):
    """
    Build an orthography class based on a PhonologicalVector class and a parser specification.
    
    Args:
        base_class (type): A class derived from PhonologicalVector.
        parser_spec (dict): A dictionary with the following keys:
            - fst (dict): A minilanguage definition for the FST.
            - substitutions (list): A list of (easy, hard) pairs for substitutions.
            - keys (list): A list of feature names.
            - parse (str): The variable name of the FST to use for parsing.
            - generate (str): The variable name of the FST to use for generation.
            
    Returns:
        type: A new class derived from base_class with orthography functionality.
    """
    class Orthography(base_class):
        """
        A class for parsing and generating orthographic representations with debugging capabilities.
        """
        # Compile the FST once and store it in the class
        syllable_fst = translate_minilanguage(parser_spec['fst'])
        
        # Class-level debug flag
        debug_mode = False
        
        @classmethod
        def set_debug_mode(cls, enabled=True):
            """
            Enable or disable debug mode for the orthography class.
            
            Args:
                enabled (bool): Whether to enable debugging.
            """
            cls.debug_mode = enabled
            if enabled:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.WARNING)
            return enabled

        def __init__(self, input_data, debug=False):
            """
            Initialize an Orthography.
            
            Args:
                input_data: Either a string to parse, a namedtuple of the base class's type,
                    or an instance of the base class.
                debug (bool): Enable debug for this specific instance.
                    
            Raises:
                TypeError: If input_data is not of a valid type.
                ValueError: If the input string cannot be parsed.
            """
            # Instance-level debug flag
            self._debug = debug or self.__class__.debug_mode
            
            if self._debug:
                logger.debug(f"Initializing with input: {input_data} (type: {type(input_data).__name__})")
                
            if isinstance(input_data, str):
                parsed_data = string_to_tuple(input_data, parser_spec, self.syllable_fst, debug=self._debug)
                named_tuple_data = self.namedtuple_type(**parsed_data)
                if self._debug:
                    logger.debug(f"Parsed string '{input_data}' to features: {parsed_data}")
                super().__init__(named_tuple_data)
            elif isinstance(input_data, self.namedtuple_type):
                if self._debug:
                    logger.debug(f"Using provided namedtuple directly: {input_data}")
                super().__init__(input_data)
            elif isinstance(input_data, base_class):
                if self._debug:
                    logger.debug(f"Using provided base class instance: {input_data}")
                super().__init__(input_data.data)
            else:
                if self._debug:
                    logger.debug(f"Invalid input type: {type(input_data).__name__}")
                raise TypeError("Invalid input type.")

        def output(self, debug=None):
            """
            Generate an orthographic representation.
            
            Args:
                debug (bool, optional): Override debug setting for this operation.
                
            Returns:
                str: The orthographic representation.
            """
            return str(self)
            
        def __str__(self):
            """
            Generate an orthographic representation.
            
            Returns:
                str: The orthographic representation.
            """
            debug_setting = self._debug
            t = [self.data._asdict()[key] for key in parser_spec['keys']]
            result = tuple_to_string(t, parser_spec, self.syllable_fst, debug=debug_setting)
            return result
            
        def __repr__(self):
            """
            Return a string representation of the orthography for debugging.
            
            Returns:
                str: The string representation.
            """
            return f'{self.reconstruction_id}({str(self)})'
            
        @classmethod
        def parse_all(cls, s, debug=None):
            """
            Parse a string into multiple orthographies.
            
            Args:
                s (str): The string to parse.
                debug (bool, optional): Enable debug for this operation.
                
            Returns:
                list: A list of Orthography instances.
            """
            debug_setting = debug if debug is not None else cls.debug_mode
            if debug_setting:
                logger.debug(f"Parsing multiple syllables: '{s}'")
                
            parsed_data = string_to_tuples(s, parser_spec, cls.syllable_fst, debug=debug_setting)
            # Keep the original order by not sorting
            named_tuples = [cls.namedtuple_type(**tup) for tup in parsed_data]
            result = []
            for i, tup in enumerate(named_tuples):
                try:
                    if debug_setting:
                        logger.debug(f"Creating instance {i+1}/{len(named_tuples)} with: {tup}")
                    result.append(cls(tup, debug=debug_setting))
                except ValueError as e:
                    if debug_setting:
                        logger.debug(f"Failed to create instance with {tup}: {str(e)}")
                    pass
            return result
            
        def debug_features(self):
            """
            Print detailed feature information for debugging purposes.
            
            Returns:
                dict: The feature dictionary.
            """
            features = self.data._asdict()
            logger.debug("Feature breakdown:")
            for key, value in features.items():
                logger.debug(f"  {key}: {value}")
            return features

    def string_to_tuple(s, parser_spec, syllable_fst, debug=False):
        """
        Parse a string into a dictionary of feature values.
        
        Args:
            s (str): The string to parse.
            parser_spec (dict): The parser specification.
            syllable_fst (dict): The compiled FSTs.
            debug (bool): Enable debugging output.
            
        Returns:
            dict: A dictionary mapping feature names to values.
            
        Raises:
            ValueError: If the string cannot be parsed.
        """
        if debug:
            logger.debug(f"Parsing string: '{s}'")
            
        substitutions = parser_spec['substitutions']
        if 'substitutions_parse' in parser_spec:
            substitutions = parser_spec['substitutions_parse']
            if debug:
                logger.debug(f"Using parse-specific substitutions: {substitutions}")
                
        # First try without substitutions
        result = fst_down(syllable_fst[parser_spec['parse']], s)
        if debug:
            if result:
                logger.debug(f"Parsed successfully without substitutions: {result[0]}")
            else:
                logger.debug("Initial parse failed, trying with substitutions")

        # Try with substitutions if initial parse failed
        for easy, hard in reversed(substitutions):
            if result:
                break
            if debug:
                logger.debug(f"Applying substitution: '{hard}' -> '{easy}'")
                
            if 'substitutions_parse' in parser_spec:
                modified = re.sub(hard, easy, s)
            else:
                modified = s.replace(hard, easy)
                
            if debug and modified != s:
                logger.debug(f"Modified input: '{s}' -> '{modified}'")
                
            result = fst_down(syllable_fst[parser_spec['parse']], modified)
            if debug:
                if result:
                    logger.debug(f"Parse succeeded after substitution: {result[0]}")
                else:
                    logger.debug(f"Parse still failed after substitution")
    
        if not result:
            error_msg = f"Could not parse '{s}'"
            if debug:
                logger.debug(f"ERROR: {error_msg}")
            raise ValueError(error_msg)
            
        feature_values = result[0].split('*')
        m = dict(zip(parser_spec['keys'], feature_values))
        
        if debug:
            logger.debug(f"Final feature mapping:")
            for k, v in m.items():
                logger.debug(f"  {k}: {v}")
                
        # Assuming we take the first result as correct and align with the namedtuple's keys
        return m
        
    def string_to_tuples(s, parser_spec, syllable_fst, debug=False):
        """
        Parse a string into multiple dictionaries of feature values.
        
        Args:
            s (str): The string to parse.
            parser_spec (dict): The parser specification.
            syllable_fst (dict): The compiled FSTs.
            debug (bool): Enable debugging output.
            
        Returns:
            list: A list of dictionaries mapping feature names to values.
        """
        # Split the input string by whitespace to handle multiple syllables
        syllables = s.split()
        all_results = []
        
        if debug:
            logger.debug(f"Splitting input '{s}' into {len(syllables)} syllables: {syllables}")
        
        for i, syllable in enumerate(syllables):
            try:
                if debug:
                    logger.debug(f"Processing syllable {i+1}/{len(syllables)}: '{syllable}'")
                # Parse each syllable individually
                parsed = string_to_tuple(syllable, parser_spec, syllable_fst, debug=debug)
                all_results.append(parsed)
                if debug:
                    logger.debug(f"Successfully parsed syllable '{syllable}'")
            except ValueError as e:
                if debug:
                    logger.debug(f"Failed to parse syllable '{syllable}': {str(e)}")
                # Skip syllables that can't be parsed
                pass
                
        if debug:
            logger.debug(f"Parsed {len(all_results)}/{len(syllables)} syllables successfully")
                
        return all_results

    def tuple_to_string(t, parser_spec, syllable_fst, debug=False):
        """
        Generate an orthographic representation from a tuple of feature values.
        
        Args:
            t (list): A list of feature values.
            parser_spec (dict): The parser specification.
            syllable_fst (dict): The compiled FSTs.
            debug (bool): Enable debugging output.
            
        Returns:
            str: The orthographic representation.
        """
        if debug:
            logger.debug(f"Generating string from feature values: {t}")
            
        s = '*'.join(t)
        if debug:
            logger.debug(f"Feature string for FST: '{s}'")
            
        result = fst_up(syllable_fst[parser_spec['generate']], s)
        
        if debug:
            if result:
                logger.debug(f"Raw generation result: {result}")
            else:
                logger.debug("Generation failed")
                
        for easy, hard in parser_spec['substitutions']:
            if debug and easy in result[0]:
                logger.debug(f"Applying substitution: '{easy}' -> '{hard}'")
            result = [res.replace(easy, hard) for res in result]
            
        if debug:
            logger.debug(f"Final orthographic form: '{result[0]}'")
            
        return result[0]

    return Orthography 