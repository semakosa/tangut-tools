"""
Finite State Transducer utilities.

This module provides utilities for working with Finite State Transducers (FSTs)
using the pyfoma library.
"""

from pyfoma.fst import FST
from functools import reduce

def translate_minilanguage(minilang):
    """
    Translate a minilanguage definition into a set of FSTs.
    
    Args:
        minilang (dict): A dictionary mapping variable names to definitions.
        
    Returns:
        dict: A dictionary mapping variable names to compiled FSTs.
    """
    translations = {key: None for key in minilang}
    SEP = FST(label=('',)) ** FST(label=('*',))  # Cross from empty string to one single asterisk

    def translate_string(s):
        if s == '':
            return FST(label=('',))
        fsts = [FST(label=(c,)) for c in s]
        return reduce(lambda x, y: x.concatenate(y), fsts)
    
    def translate(item):
        if isinstance(item, str):
            if item in translations:  # variable name
                if translations[item] is None:
                    translate_var(item)
                return translations[item]
            elif item == '*':
                return SEP
            elif ':' in item:
                a, b = item.split(':', 1)
                return translate_string(a) ** translate_string(b)
            else:
                return translate_string(item)
        elif isinstance(item, dict):
            if 'union' in item:
                items = [translate(i) for i in item['union']]
                result = items[0].__copy__()
                for i in items[1:]:
                    result = result | i
                return result
            elif 'concat' in item:
                items = [translate(i) for i in item['concat']]
                result = items[0].__copy__()
                for i in items[1:]:
                    result = result * i
                return result
        raise ValueError(f'Unknown item type: {item}')

    def translate_var(var_name):
        translation = translate(minilang[var_name])
        translations[var_name] = translation.minimize()

    for var_name in minilang:
        translate_var(var_name)
    return translations


def fst_down(fst, s):
    """
    Apply an FST to a string in the downward direction.
    
    Args:
        fst (FST): The FST to apply.
        s (str): The string to apply the FST to.
        
    Returns:
        list: A list of output strings.
    """
    results = list(fst.apply(s, inverse=False))
    return results


def fst_up(fst, s):
    """
    Apply an FST to a string in the upward direction.
    
    Args:
        fst (FST): The FST to apply.
        s (str): The string to apply the FST to.
        
    Returns:
        list: A list of output strings.
    """
    results = list(fst.apply(s, inverse=True))
    return results 