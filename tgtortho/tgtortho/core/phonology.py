"""
Phonological vector module.

This module provides the base classes and functions for creating phonological
vectors.
"""

from collections import namedtuple


class PhonologicalVector:
    """
    A class representing a phonological vector.
    
    This class stores phonological data as a namedtuple and provides dictionary-like
    access to the phonological features with validation based on the specification.
    
    Attributes:
        namedtuple_type (namedtuple): The namedtuple type used to store the data.
        specification (dict): A dictionary specifying valid values for each feature.
        reconstruction_id (str): The ID of the reconstruction model.
    """
    
    # The namedtuple type will be created outside of the class, stored as a class variable.
    namedtuple_type = None
    specification = {}  # This should be defined with the specific keys and valid values
    reconstruction_id = None

    def __init__(self, input_vector):
        """
        Initialize a PhonologicalVector.
        
        Args:
            input_vector: Either a namedtuple of the type specified by namedtuple_type,
                          or a dictionary mapping feature names to values.
            
        Raises:
            TypeError: If input_vector is not of the correct type.
            ValueError: If any value in input_vector is not valid according to the specification.
        """
        # Handle dictionary input
        if isinstance(input_vector, dict):
            # Convert dictionary to namedtuple
            try:
                nt_data = self.namedtuple_type(**input_vector)
                self._validate_vector(nt_data)
                self.data = nt_data
            except TypeError as e:
                missing = set(self.namedtuple_type._fields) - set(input_vector.keys())
                if missing:
                    raise ValueError(f"Missing required features: {', '.join(missing)}") from e
                raise
        # Handle namedtuple input (backward compatibility)
        elif isinstance(input_vector, self.namedtuple_type):
            self._validate_vector(input_vector)
            self.data = input_vector
        # Handle another PhonologicalVector instance
        elif isinstance(input_vector, PhonologicalVector):
            self._validate_vector(input_vector.data)
            self.data = input_vector.data
        else:
            raise TypeError(f"Input must be a dictionary, a '{self.namedtuple_type.__name__}' namedtuple, "
                           f"or a PhonologicalVector instance")

    def _validate_vector(self, input_vector):
        """
        Validate that all values in the input_vector are valid according to the specification.
        
        Args:
            input_vector (namedtuple): The vector to validate.
            
        Raises:
            ValueError: If any value is not valid.
        """
        for key, value in input_vector._asdict().items():
            if key not in self.specification:
                raise ValueError(f"Unknown feature: '{key}'")
            if value not in self.specification[key]:
                raise ValueError(f"Invalid value '{value}' for feature '{key}'. Valid values are: {self.specification[key]}")

    def __getitem__(self, item):
        """
        Get a feature value.
        
        Args:
            item (str): The feature name.
            
        Returns:
            The feature value.
        """
        return getattr(self.data, item)

    def __setitem__(self, key, value):
        """
        Set a feature value.
        
        Args:
            key (str): The feature name.
            value: The new value.
            
        Raises:
            ValueError: If the key is not valid or the value is not valid for the key.
        """
        if key in self.specification:
            if value in self.specification[key]:
                # Create a new namedtuple with the updated value
                updated_data = self.data._replace(**{key: value})
                self.data = updated_data
            else:
                raise ValueError(f"Invalid value '{value}' for feature '{key}'. Valid values are: {self.specification[key]}")
        else:
            raise ValueError(f"Feature '{key}' is not valid. Valid features are: {', '.join(self.specification.keys())}")

    def __len__(self):
        """Return the number of features."""
        return len(self.data)

    def __iter__(self):
        """Iterate over feature names."""
        return iter(self.data._asdict())

    def __contains__(self, item):
        """Check if a feature name exists."""
        return item in self.data._asdict()

    def keys(self):
        """Return the feature names."""
        return self.data._asdict().keys()

    def values(self):
        """Return the feature values."""
        return self.data._asdict().values()

    def items(self):
        """Return the feature name-value pairs."""
        return self.data._asdict().items()

    def get(self, key, default=None):
        """
        Get a feature value, or a default if the feature doesn't exist.
        
        Args:
            key (str): The feature name.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The feature value, or the default.
        """
        return self.data._asdict().get(key, default)

    def __eq__(self, other):
        """
        Check if two PhonologicalVectors are equal.
        
        Args:
            other (PhonologicalVector): The other vector.
            
        Returns:
            bool: True if the vectors are equal, False otherwise.
        """
        if isinstance(other, PhonologicalVector):
            return self.data == other.data
        return NotImplemented

    def __ne__(self, other):
        """Check if two PhonologicalVectors are not equal."""
        return not self.__eq__(other)

    def update(self, *args, **kwargs):
        """
        Update multiple features at once.
        
        Args:
            *args: Dictionary of updates.
            **kwargs: Keyword arguments with feature updates.
            
        Raises:
            ValueError: If any key or value is not valid.
        """
        # Create a dictionary from current data
        updated_data = self.data._asdict()
        
        # Update with new values
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 argument, got %d" % len(args))
            other = args[0]
            if isinstance(other, dict):
                updated_data.update(other)
            elif hasattr(other, "keys"):
                for key in other:
                    updated_data[key] = other[key]
            else:
                for key, value in other:
                    updated_data[key] = value
        
        # Update with keyword arguments
        updated_data.update(kwargs)
        
        # Create a new namedtuple and validate
        new_namedtuple = self.namedtuple_type(**updated_data)
        self._validate_vector(new_namedtuple)
        self.data = new_namedtuple

    def to_dict(self):
        """
        Convert the phonological vector to a dictionary.
        
        Returns:
            dict: A dictionary representation of the phonological vector.
        """
        return self.data._asdict()

    def __str__(self):
        """Return a string representation of the vector."""
        features = self.data._asdict()
        return f"{self.reconstruction_id}({', '.join(f'{k}={v}' for k, v in features.items())})"
        
    def __repr__(self):
        """Return a string representation of the vector for debugging."""
        return f"{self.reconstruction_id}{tuple(self.data)}"


def build_phonological_vector_class(spec):
    """
    Dynamically create a PhonologicalVector class based on a specification.
    
    Args:
        spec (dict): A dictionary with the following keys:
            - reconstruction_id (str): The ID of the reconstruction model.
            - specification (dict): A dictionary mapping feature names to lists of valid values.
            
    Returns:
        type: A new class derived from PhonologicalVector.
    """
    # Create a namedtuple with the given specification fields
    namedtuple_type = namedtuple(f"{spec['reconstruction_id']}_Vector", spec['specification'].keys())

    # Create a specification dict that includes the reconstruction_id
    full_spec = spec['specification'].copy()
    
    # Define a new class with a custom namedtuple and specification
    new_class = type(f"PhonologicalVector_{spec['reconstruction_id']}", (PhonologicalVector,), {
        'reconstruction_id': spec['reconstruction_id'],
        'specification': full_spec,
        'namedtuple_type': namedtuple_type,
    })

    return new_class 