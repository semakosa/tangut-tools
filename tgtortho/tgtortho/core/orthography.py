"""
Orthography module.

This module provides functions for building orthography classes based on
phonological vector classes and parser specifications, with debugging capabilities.
It includes comprehensive FST structure validation to ensure proper feature mapping.
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
    
    This function performs several validations on the FST structure:
    1. Checks that all union branches within the same variable have the same number of separators
    2. Verifies that entry points have the expected number of separators for the given keys
    3. Maps each FST component to the features it handles based on its position in the structure
    
    Args:
        fst_defs (dict): The FST minilanguage definitions.
        keys (list): The list of feature names in the model specification.
        parse_entry (str): The entry point variable name for parsing.
        generate_entry (str): The entry point variable name for generation.
        
    Returns:
        dict: A dictionary containing:
            - direct_separator_counts: Count of direct "*" separators in each variable
            - total_separator_counts: Count of total "*" separators including referenced variables
            - field_mappings: Mapping of variables to the feature fields they represent
            - feature_paths: Maps variables to specific feature keys they handle
            - entry_points: Analysis of parse and generate entry points
            - warnings: List of any issues found during validation
        
    Raises:
        ValueError: If the FST structure is inconsistent or invalid, such as:
            - Union branches with inconsistent separator counts
            - Invalid references to undefined variables
            - Circular references in the FST definitions
    """
    # We need to track both direct separators and total separators through the path
    direct_separator_counts = {}  # Only direct "*" in the current variable
    total_separator_counts = {}   # Including separators in referenced variables
    field_mappings = {}
    feature_paths = {}  # Maps variables to specific feature keys they handle
    
    # Track variables we've already processed to avoid infinite recursion
    processed = set()
    
    def count_direct_separators(definition):
        """
        Count the number of "*" separators directly in an FST definition (non-recursive).
        
        Args:
            definition: An FST definition (string, dict with 'union' or 'concat')
            
        Returns:
            int: The number of direct separators
        """
        if isinstance(definition, str):
            return 1 if definition == "*" else 0
        
        if isinstance(definition, dict):
            if "union" in definition:
                # For union branches, we check that all have the same direct separator count
                # but return the count of the first branch as representative
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
        
        Args:
            var_name (str): The name of the FST variable to analyze
            visited (set, optional): Set of already visited variables to prevent infinite recursion
            
        Returns:
            int: The total number of separators
            
        Raises:
            ValueError: If union branches have inconsistent separator counts
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
                # All branches should have same total separators - this is a requirement
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
                    raise ValueError(f"Inconsistent total separator count in union branches of {var_name}: {counts}. All branches must have the same number of separators.")
                
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
    
    # For entry points, map the entire set of keys
    entry_points = [parse_entry, generate_entry]
    for entry_point in entry_points:
        if entry_point in fst_defs:
            feature_paths[entry_point] = keys.copy()
    
    # Map components based on their position in the concatenation pattern
    def map_components_from_pattern(var_name):
        """
        Map features to components based on their position in the concatenation pattern.
        
        This method distributes feature keys to FST components based on their 
        position in the entry point's concatenation structure and their
        separator counts. Each component is mapped to the features it handles.
        
        Args:
            var_name (str): The name of the FST variable to analyze
            
        Returns:
            None: Updates feature_paths dictionary in-place
        """
        if var_name not in fst_defs:
            return
            
        definition = fst_defs[var_name]
        if not isinstance(definition, dict) or "concat" not in definition:
            return
            
        components = definition["concat"]
        current_feature_index = 0
        
        for i, component in enumerate(components):
            if isinstance(component, str):
                if component == "*":
                    # Skip separators
                    continue
                elif component in fst_defs:
                    # This is a component variable, map it to its feature
                    # Count how many features this component should take
                    seps = total_separator_counts.get(component, 0)
                    num_features = seps + 1
                    
                    # Map the appropriate number of features
                    if current_feature_index < len(keys):
                        end_index = min(current_feature_index + num_features, len(keys))
                        feature_paths[component] = keys[current_feature_index:end_index]
                        
                        # Also map any nested components
                        map_components_from_pattern(component)
                        
                    # Move to the next set of features
                    current_feature_index += num_features
    
    # Map components for entry points
    for entry_point in entry_points:
        map_components_from_pattern(entry_point)
    
    # Special handling for variables without features mapped yet
    # Try name-based matching for any remaining variables
    for var_name in fst_defs:
        if var_name not in feature_paths:
            # Try simple name-based matching as a fallback
            matching_features = []
            for key in keys:
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
                    
            if matching_features:
                feature_paths[var_name] = matching_features
    
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
    
    This function creates a new class derived from the base class, adding functionality
    for parsing strings into phonological feature vectors and generating orthographic
    representations from those vectors. It also validates the FST structure to ensure
    consistent feature mapping.
    
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
        
    Notes:
        The FST structure validation ensures that:
        - Each union branch in a variable has the same total number of separators
        - Entry points have the expected number of separators for the given keys
        - FST components are mapped to the features they handle
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
        
        This class extends a PhonologicalVector class to add capabilities for:
        - Parsing orthographic strings into phonological feature vectors
        - Generating orthographic representations from phonological feature vectors
        - Validating and visualizing the FST structure
        - Debugging the parsing and generation process
        
        The class uses a finite-state transducer (FST) to handle the mapping between
        orthographic forms and phonological features.
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
            
            When debug mode is enabled, detailed logging information is provided
            about the parsing and generation process.
            
            Args:
                enabled (bool): Whether to enable debugging.
                
            Returns:
                bool: The new debug mode state.
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
                dict: The FST structure analysis or None if not available.
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
            
            # FST Component Structure section
            lines.append("FST Component Structure:")
            
            # Try to extract the components from the Syllable (or other entry point) definition
            entry_point = entry_points['parse']['variable']
            fst_defs = cls.parser_specification['fst']
            
            # Find the components in order of appearance
            components_order = []
            if entry_point in fst_defs and isinstance(fst_defs[entry_point], dict) and "concat" in fst_defs[entry_point]:
                concat_items = fst_defs[entry_point]["concat"]
                # Extract component names (ignoring separators)
                for item in concat_items:
                    if isinstance(item, str) and item != "*" and item in fst_defs:
                        components_order.append(item)
            
            # Add entry point first
            lines.append(f"  {entry_point}: → All features")
            
            # Display components in order from the entry point
            for component in components_order:
                if component in feature_paths:
                    features_str = ", ".join(feature_paths[component])
                    total_count = total_separator_counts.get(component, 0)
                    direct_count = direct_separator_counts.get(component, 0)
                    
                    separator_info = f"{total_count} total separators"
                    if direct_count != total_count:
                        separator_info += f" ({direct_count} direct, {total_count-direct_count} indirect)"
                    
                    lines.append(f"  └─ {component}: {separator_info}")
                    lines.append(f"     Features: {features_str}")
            
            # Display other variables with feature mappings
            other_vars = [v for v in feature_paths if v != entry_point and v not in components_order]
            if other_vars:
                lines.append("\nOther Variables with Feature Mappings:")
                for var_name in sorted(other_vars):
                    features_str = ", ".join(feature_paths[var_name])
                    total_count = total_separator_counts.get(var_name, 0)
                    direct_count = direct_separator_counts.get(var_name, 0)
                    
                    separator_info = f"{total_count} total separators"
                    if direct_count != total_count:
                        separator_info += f" ({direct_count} direct, {total_count-direct_count} indirect)"
                    
                    lines.append(f"  {var_name}: {separator_info}")
                    lines.append(f"    Features: {features_str}")
            
            # Handle variables without feature mappings
            unmapped_vars = [v for v in total_separator_counts if v not in feature_paths]
            if unmapped_vars:
                lines.append("\nUnmapped Variables:")
                for var_name in sorted(unmapped_vars):
                    total_count = total_separator_counts.get(var_name, 0)
                    direct_count = direct_separator_counts.get(var_name, 0)
                    
                    separator_info = f"{total_count} total separators"
                    if direct_count != total_count:
                        separator_info += f" ({direct_count} direct, {total_count-direct_count} indirect)"
                    
                    lines.append(f"  {var_name}: {separator_info}")
            
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
        modified = s
        for easy, hard in reversed(substitutions):
            if result:
                break
                
            if 'substitutions_parse' in parser_spec:
                if debug:
                    logger.debug(f"re.sub: {hard} -> {easy}, {modified}")
                modified = re.sub(hard, easy, modified)
            else:
                if debug:
                    logger.debug(f"'{modified}'.replace: {hard} -> {easy}")
                modified = modified.replace(hard, easy)
                
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