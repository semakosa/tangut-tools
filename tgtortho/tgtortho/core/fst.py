"""
Finite State Transducer utilities.

This module provides utilities for working with Finite State Transducers (FSTs)
using the pynini library.
"""

import pynini


def translate_minilanguage(minilang):
    """
    Translate a minilanguage definition into a set of FSTs.
    
    Args:
        minilang (dict): A dictionary mapping variable names to definitions.
        
    Returns:
        dict: A dictionary mapping variable names to compiled FSTs.
    """
    translations = {key: None for key in minilang}
    SEP = pynini.cross("", "*")
    
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
                return pynini.cross(a, b)
            else:
                return item
        elif isinstance(item, dict):
            if 'union' in item:
                items = [translate(i) for i in item['union']]
                return pynini.union(*items)
            elif 'concat' in item:
                items = [translate(i) for i in item['concat']]
                result = items[0]
                for i in items[1:]:
                    result = pynini.concat(result, i)
                return result
        raise ValueError(f'Unknown item type: {item}')

    def translate_var(var_name):
        translation = translate(minilang[var_name])
        translations[var_name] = translation.optimize()

    for var_name in minilang:
        translate_var(var_name)
    return translations


def fst_down(fst, s):
    """
    Apply an FST to a string in the downward direction.
    
    Args:
        fst (pynini.Fst): The FST to apply.
        s (str): The string to apply the FST to.
        
    Returns:
        list: A list of output strings.
    """
    return list(pynini.compose(s, fst).paths().ostrings())


def fst_up(fst, s):
    """
    Apply an FST to a string in the upward direction.
    
    Args:
        fst (pynini.Fst): The FST to apply.
        s (str): The string to apply the FST to.
        
    Returns:
        list: A list of output strings.
    """
    return list(pynini.compose(s, pynini.invert(fst)).paths().ostrings()) 