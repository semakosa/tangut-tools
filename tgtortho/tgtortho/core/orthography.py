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

def validate_fst_structure(fst_defs, keys, parse_entry, generate_entry):
    """
    Validate FST structure by checking the consistency of "*" separators
    and mapping FST variables to their corresponding feature fields.
    
    Args:
        fst_defs (dict): The FST minilanguage definitions.
        keys (list): The list of feature names in the model specification.
        parse_entry (str): The entry point for parsing.
        generate_entry (str): The entry point for generation.
        
    Returns:
        dict: Mapping of FST variables to the feature fields they represent.
        
    Raises:
        ValueError: If FST structure is inconsistent or invalid.
    """
    # We need to track both direct separators and total separators through the path
    direct_separator_counts = {}  # Only direct "*" in the current variable
    total_separator_counts = {}   # Including separators in referenced variables
    field_mappings = {}
    feature_paths = {}  # Maps variables to specific feature keys they handle
    
    # Track variables we've already processed to avoid infinite recursion
    processed = set()
    
    def count_direct_separators(definition):
        """Count the number of "*" separators directly in an FST definition (non-recursive)."""
        if isinstance(definition, str):
            return 1 if definition == "*" else 0
        
        if isinstance(definition, dict):
            if "union" in definition:
                # For union branches, we only need to count direct separators
                # but we don't enforce consistency here - that's for total separators
                counts = [count_direct_separators(item) for item in definition["union"]]
                return counts[0] if counts else 0
            
            elif "concat" in definition:
                # Sum separator counts in concatenation
                return sum(count_direct_separators(item) for item in definition["concat"])
        
        return 0
    
    def count_total_separators(var_name, visited=None):
        """
        Recursively count the total "*" separators in an FST variable definition,
        including those in referenced variables.
        """
        if visited is None:
            visited = set()
            
        # Avoid infinite recursion
        if var_name in visited:
            return 0
        
        # Use cached result if available
        if var_name in total_separator_counts:
            return total_separator_counts[var_name]
            
        visited.add(var_name)
        definition = fst_defs[var_name]
        
        # For string references to other variables
        if isinstance(definition, str):
            if definition == "*":
                return 1
            elif definition in fst_defs:
                # Recursively count separators in the referenced variable
                return count_total_separators(definition, visited)
            else:
                return 0
                
        # For dictionary definitions
        elif isinstance(definition, dict):
            if "union" in definition:
                # All branches should have same total separators
                items = definition["union"]
                counts = []
                
                for item in items:
                    if isinstance(item, str):
                        if item == "*":
                            counts.append(1)
                        elif item in fst_defs:
                            counts.append(count_total_separators(item, visited.copy()))
                        else:
                            counts.append(0)
                    elif isinstance(item, dict):
                        if "concat" in item:
                            count = 0
                            for concat_item in item["concat"]:
                                if isinstance(concat_item, str):
                                    if concat_item == "*":
                                        count += 1
                                    elif concat_item in fst_defs:
                                        count += count_total_separators(concat_item, visited.copy())
                                elif isinstance(concat_item, dict):
                                    # Recursively handle nested dictionaries
                                    temp_var = f"_temp_{len(fst_defs)}"
                                    fst_defs[temp_var] = concat_item
                                    count += count_total_separators(temp_var, visited.copy())
                                    del fst_defs[temp_var]
                            counts.append(count)
                
                if counts and len(set(counts)) > 1:
                    raise ValueError(f"Inconsistent total separator count in union branches of {var_name}: {counts}")
                
                total = counts[0] if counts else 0
                total_separator_counts[var_name] = total
                return total
                
            elif "concat" in definition:
                # Sum separator counts in concatenation
                total = 0
                for item in definition["concat"]:
                    if isinstance(item, str):
                        if item == "*":
                            total += 1
                        elif item in fst_defs:
                            total += count_total_separators(item, visited.copy())
                    elif isinstance(item, dict):
                        # Recursively handle nested dictionaries
                        temp_var = f"_temp_{len(fst_defs)}"
                        fst_defs[temp_var] = item
                        total += count_total_separators(temp_var, visited.copy())
                        del fst_defs[temp_var]
                
                total_separator_counts[var_name] = total
                return total
        
        return 0
    
    def track_features_in_path(var_name, current_path=None, start_index=0, visited=None):
        """
        Track the specific feature keys each FST variable corresponds to.
        
        Args:
            var_name: The FST variable name to analyze
            current_path: List of features encountered so far in the path
            start_index: Current feature index in the path
            visited: Set of already visited variables to prevent cycles
            
        Returns:
            list: The feature indices this variable handles
            int: The new index after processing this variable
        """
        if visited is None:
            visited = set()
            
        if current_path is None:
            current_path = []
            
        # Avoid infinite recursion
        if var_name in visited:
            return current_path, start_index
            
        visited.add(var_name)
        definition = fst_defs[var_name]
        
        # For simple string references
        if isinstance(definition, str):
            if definition == "*":
                # This is a separator, represent both features it separates
                return [start_index, start_index + 1], start_index + 1
            elif definition in fst_defs and definition not in visited:
                # Recursively process referenced variable
                return track_features_in_path(definition, current_path, start_index, visited)
            else:
                # String literal, corresponds to the current feature
                return [start_index], start_index
        
        # For dictionary definitions
        elif isinstance(definition, dict):
            if "union" in definition:
                # For union, take the first branch's path (should be consistent across branches)
                items = definition["union"]
                if items:
                    # Use first item as representative (all branches should handle same features)
                    item = items[0]
                    if isinstance(item, str):
                        if item == "*":
                            return [start_index, start_index + 1], start_index + 1
                        elif item in fst_defs and item not in visited:
                            return track_features_in_path(item, current_path, start_index, visited)
                    elif isinstance(item, dict) and "concat" in item:
                        # Handle concatenation within union
                        this_path = []
                        idx = start_index
                        for concat_item in item["concat"]:
                            if isinstance(concat_item, str):
                                if concat_item == "*":
                                    this_path.append(idx)
                                    this_path.append(idx + 1)
                                    idx += 1
                                elif concat_item in fst_defs and concat_item not in visited:
                                    sub_path, idx = track_features_in_path(concat_item, this_path, idx, visited.copy())
                                    this_path.extend(sub_path)
                            elif isinstance(concat_item, dict):
                                # Handle nested dictionaries
                                temp_var = f"_temp_{len(fst_defs)}"
                                fst_defs[temp_var] = concat_item
                                sub_path, idx = track_features_in_path(temp_var, this_path, idx, visited.copy())
                                this_path.extend(sub_path)
                                del fst_defs[temp_var]
                        return this_path, idx
                
                return [], start_index
                
            elif "concat" in definition:
                # For concatenation, process items in sequence
                items = definition["concat"]
                this_path = []
                idx = start_index
                
                for item in items:
                    if isinstance(item, str):
                        if item == "*":
                            # Separator marks a feature boundary
                            # Include both features it separates
                            this_path.append(idx)
                            this_path.append(idx + 1)
                            idx += 1
                        elif item in fst_defs and item not in visited:
                            # Process referenced variable
                            sub_path, idx = track_features_in_path(item, [], idx, visited.copy())
                            this_path.extend(sub_path)
                    elif isinstance(item, dict):
                        # Handle nested dictionaries
                        temp_var = f"_temp_{len(fst_defs)}"
                        fst_defs[temp_var] = item
                        sub_path, idx = track_features_in_path(temp_var, [], idx, visited.copy())
                        this_path.extend(sub_path)
                        del fst_defs[temp_var]
                
                return this_path, idx
        
        return [], start_index
    
    # First pass: count direct separators in each variable
    for var_name, definition in fst_defs.items():
        try:
            count = count_direct_separators(definition)
            direct_separator_counts[var_name] = count
        except ValueError as e:
            # Re-raise with variable name for better debugging
            raise ValueError(f"Error in FST variable '{var_name}': {str(e)}")
    
    # Second pass: recursively count total separators through the entire path
    for var_name in fst_defs:
        try:
            if var_name not in total_separator_counts:
                count_total_separators(var_name)
        except ValueError as e:
            # Re-raise with variable name for better debugging
            raise ValueError(f"Error in recursive analysis of '{var_name}': {str(e)}")
    
    # Third pass: track which features each variable corresponds to
    for var_name in fst_defs:
        try:
            indices, _ = track_features_in_path(var_name)
            
            # Filter out any duplicates and sort
            indices = sorted(set(indices))
            
            # Map indices to actual feature names
            if indices:
                feature_keys = [keys[i] for i in indices if i < len(keys)]
                if feature_keys:
                    feature_paths[var_name] = feature_keys
            # For variables that don't map to any indices directly, but have a relevant name
            elif total_separator_counts.get(var_name, 0) == 0:
                # Try to match by name
                matching_features = []
                for i, key in enumerate(keys):
                    # Exact match
                    if var_name.lower() == key.lower():
                        matching_features = [key]
                        break
                    # Variable name contains feature name
                    elif key.lower() in var_name.lower():
                        matching_features.append(key)
                    # Feature name contains variable name
                    elif var_name.lower() in key.lower():
                        matching_features.append(key)
                
                # Special cases based on common naming patterns
                if not matching_features:
                    if 'vowel' in var_name.lower():
                        for key in keys:
                            if '元音' in key:  # '元音' means vowel
                                matching_features.append(key)
                    elif 'initial' in var_name.lower() or 'consonant' in var_name.lower():
                        for key in keys:
                            if '声母' in key:  # '声母' means initial consonant
                                matching_features.append(key)
                    elif 'tone' in var_name.lower():
                        for key in keys:
                            if '声调' in key:  # '声调' means tone
                                matching_features.append(key)
                    elif 'coda' in var_name.lower() or 'final' in var_name.lower():
                        for key in keys:
                            if '韵尾' in key:  # '韵尾' means coda/final
                                matching_features.append(key)
                    elif 'round' in var_name.lower():
                        for key in keys:
                            if '合口' in key:  # '合口' means rounding
                                matching_features.append(key)
                
                if matching_features:
                    feature_paths[var_name] = matching_features
        except Exception as e:
            # Log the error but continue processing
            logger.warning(f"Error tracking features for '{var_name}': {str(e)}")
    
    # Analyze the field mappings
    for var_name, definition in fst_defs.items():
        # For concatenation rules, try to infer field mappings based on recursive separator count
        if isinstance(definition, dict) and "concat" in definition:
            total_seps = total_separator_counts.get(var_name, 0)
            
            # The number of fields is always separator_count + 1
            # Even a variable with 0 separators corresponds to 1 feature
            num_fields = total_seps + 1
            
            # If this variable covers all fields, map it to the full key set
            if num_fields == len(keys):
                field_mappings[var_name] = keys.copy()
            # For partial matches, get from feature_paths if available
            elif var_name in feature_paths:
                field_mappings[var_name] = feature_paths[var_name]
    
    # Special handling for entry points - they should cover all fields
    entry_points_analysis = {
        "parse": {
            "variable": parse_entry,
            "direct_separator_count": direct_separator_counts.get(parse_entry, 0),
            "total_separator_count": total_separator_counts.get(parse_entry, 0),
            "expected_count": len(keys) - 1,  # Expected separator count should be len(keys) - 1
            "features": feature_paths.get(parse_entry, [])
        },
        "generate": {
            "variable": generate_entry,
            "direct_separator_count": direct_separator_counts.get(generate_entry, 0),
            "total_separator_count": total_separator_counts.get(generate_entry, 0),
            "expected_count": len(keys) - 1,
            "features": feature_paths.get(generate_entry, [])
        }
    }
    
    # Validate entry points
    warnings = []
    
    # Check parse entry point
    if parse_entry not in total_separator_counts:
        warnings.append(f"Parse entry point '{parse_entry}' not found in FST definitions")
    elif total_separator_counts[parse_entry] != len(keys) - 1:
        warnings.append(f"Parse entry point '{parse_entry}' has {total_separator_counts[parse_entry]} total separators, " +
                       f"but should have {len(keys) - 1} for {len(keys)} keys")
    
    # Check generate entry point
    if generate_entry not in total_separator_counts:
        warnings.append(f"Generate entry point '{generate_entry}' not found in FST definitions")
    elif total_separator_counts[generate_entry] != len(keys) - 1:
        warnings.append(f"Generate entry point '{generate_entry}' has {total_separator_counts[generate_entry]} total separators, " +
                       f"but should have {len(keys) - 1} for {len(keys)} keys")
    
    return {
        "direct_separator_counts": direct_separator_counts,
        "total_separator_counts": total_separator_counts, 
        "field_mappings": field_mappings,
        "feature_paths": feature_paths,
        "entry_points": entry_points_analysis,
        "warnings": warnings
    }

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
    # Validate FST structure before compiling
    try:
        analysis_result = validate_fst_structure(
            parser_spec['fst'], 
            parser_spec['keys'],
            parser_spec['parse'],
            parser_spec['generate']
        )
        logger.info(f"FST validation completed")
        
        # Log the separator counts for each FST variable
        for var_name, count in analysis_result["direct_separator_counts"].items():
            logger.debug(f"FST variable '{var_name}' has {count} direct separators")
        
        for var_name, count in analysis_result["total_separator_counts"].items():
            logger.debug(f"FST variable '{var_name}' has {count} total separators")
        
        # Log the field mappings for each FST variable
        for var_name, fields in analysis_result["field_mappings"].items():
            if fields:
                logger.debug(f"FST variable '{var_name}' maps to fields: {', '.join(fields)}")
                
        # Log any warnings
        for warning in analysis_result.get("warnings", []):
            logger.warning(f"FST validation warning: {warning}")
            
    except ValueError as e:
        logger.warning(f"FST validation error: {str(e)}")
        analysis_result = None  # Ensure it's defined even in case of error

    class Orthography(base_class):
        """
        A class for parsing and generating orthographic representations with debugging capabilities.
        """
        # Compile the FST once and store it in the class
        parser_specification = parser_spec  # Store the parser spec for reference
        syllable_fst = translate_minilanguage(parser_specification['fst'])
        
        # Store the FST analysis for debugging as a class variable
        fst_analysis = analysis_result
        
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
            
        @classmethod
        def debug_fst_structure(cls):
            """
            Return the analysis of the FST structure for debugging purposes.
            
            This provides information about:
            - The number of "*" separators in each FST variable definition
            - The mapping between FST variables and feature fields
            - Analysis of entry points for parsing and generation
            - Any warnings or potential issues detected during validation
            - Specific feature keys each FST variable corresponds to
            
            Returns:
                dict: The FST structure analysis.
            """
            if not cls.fst_analysis:
                logger.warning("FST analysis information is not available")
                return None
                
            result = {
                "direct_separator_counts": dict(cls.fst_analysis["direct_separator_counts"]),
                "total_separator_counts": dict(cls.fst_analysis["total_separator_counts"]),
                "field_mappings": dict(cls.fst_analysis["field_mappings"]),
                "feature_paths": dict(cls.fst_analysis.get("feature_paths", {})),
                "entry_points": cls.fst_analysis["entry_points"],
                "warnings": list(cls.fst_analysis.get("warnings", [])),
                "keys": cls.parser_specification["keys"]
            }
            
            return result
        
        @classmethod
        def visualize_fst_structure(cls):
            """
            Create a human-readable visualization of the FST structure.
            
            This method creates a textual visualization of the FST structure,
            showing which phonological features are handled by each FST variable
            and the connections between them.
            
            Returns:
                str: A formatted string representation of the FST structure.
            """
            if not cls.fst_analysis:
                return "FST analysis information is not available"
                
            direct_separator_counts = cls.fst_analysis["direct_separator_counts"]
            total_separator_counts = cls.fst_analysis["total_separator_counts"]
            field_mappings = cls.fst_analysis["field_mappings"]
            feature_paths = cls.fst_analysis.get("feature_paths", {})
            entry_points = cls.fst_analysis["entry_points"]
            keys = cls.parser_specification["keys"]
            
            # Create a visual representation
            lines = ["FST Structure Visualization:", "=" * 30, ""]
            
            # Entry points section
            lines.append("Entry Points:")
            lines.append(f"  Parse: {entry_points['parse']['variable']} (expected: {entry_points['parse']['expected_count']} total separators, actual: {entry_points['parse']['total_separator_count']})")
            if entry_points['parse'].get('features'):
                lines.append(f"    Features: {', '.join(entry_points['parse']['features'])}")
                
            lines.append(f"  Generate: {entry_points['generate']['variable']} (expected: {entry_points['generate']['expected_count']} total separators, actual: {entry_points['generate']['total_separator_count']})")
            if entry_points['generate'].get('features'):
                lines.append(f"    Features: {', '.join(entry_points['generate']['features'])}")
            lines.append("")
            
            # Keys section
            lines.append("Feature Keys:")
            for i, key in enumerate(keys):
                lines.append(f"  {i}: {key}")
            lines.append("")
            
            # FST variables section
            lines.append("FST Variables:")
            
            # Sort by total separator count to group similar variables
            sorted_vars = sorted(total_separator_counts.items(), key=lambda x: (-x[1], x[0]))
            
            for var_name, total_count in sorted_vars:
                direct_count = direct_separator_counts.get(var_name, 0)
                separator_info = f"{total_count} total separators"
                if direct_count != total_count:
                    separator_info += f" ({direct_count} direct, {total_count-direct_count} indirect)"
                
                field_str = ""
                if var_name in feature_paths and feature_paths[var_name]:
                    field_str = f" → Features: {', '.join(feature_paths[var_name])}"
                elif var_name in field_mappings and field_mappings[var_name]:
                    field_str = f" → Fields: {', '.join(field_mappings[var_name])}"
                # For variables with 0 separators and no feature paths mapped,
                # try to infer a single feature by index in the feature list
                elif total_count == 0:
                    # We should already have feature mappings from our enhanced logic
                    # but just in case, provide a fallback
                    if var_name in feature_paths and feature_paths[var_name]:
                        field_str = f" → Features: {', '.join(feature_paths[var_name])}"
                    else:
                        # Fall back to simple name-based matching
                        matching_features = []
                        
                        # Check for common linguistic terms in the variable name
                        if 'vowel' in var_name.lower():
                            matching_features = ["元音"]  # Vowel
                        elif 'initial' in var_name.lower() or 'consonant' in var_name.lower():
                            matching_features = ["声母"]  # Initial consonant
                        elif 'tone' in var_name.lower():
                            matching_features = ["声调"]  # Tone
                        elif 'coda' in var_name.lower() or 'final' in var_name.lower():
                            matching_features = ["韵尾"]  # Coda/final
                        elif 'round' in var_name.lower():
                            matching_features = ["合口"]  # Rounding
                            
                        if matching_features:
                            field_str = f" → Features: {', '.join(matching_features)}"
                        else:
                            field_str = f" → Features: (maps to a single feature)"
                
                is_entry = ""
                if var_name == entry_points["parse"]["variable"]:
                    is_entry = " (PARSE ENTRY POINT)"
                elif var_name == entry_points["generate"]["variable"]:
                    is_entry = " (GENERATE ENTRY POINT)"
                
                lines.append(f"  {var_name}: {separator_info}{field_str}{is_entry}")
            
            # Warnings section
            if cls.fst_analysis.get("warnings"):
                lines.append("")
                lines.append("Warnings:")
                for warning in cls.fst_analysis["warnings"]:
                    lines.append(f"  • {warning}")
            
            return "\n".join(lines)
        
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
                parsed_data = string_to_tuple(input_data, self.__class__.parser_specification, self.syllable_fst, debug=self._debug)
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
            t = [self.data._asdict()[key] for key in self.__class__.parser_specification['keys']]
            result = tuple_to_string(t, self.__class__.parser_specification, self.syllable_fst, debug=debug_setting)
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
                
            parsed_data = string_to_tuples(s, cls.parser_specification, cls.syllable_fst, debug=debug_setting)
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