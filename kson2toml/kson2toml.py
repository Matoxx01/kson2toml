"""
Documentation for the Kson2toml converter.
"""
from kson import Kson
from kson2toml.ast import kson_to_toml_string

def kson2toml(kson_string):
    """
    Conversion logic from Kson to Toml would go here
    
    :param kson_string: The all Kson string

    :return toml_string: Complete conversion to Toml string
    """
    a = Kson.analyze(kson_string)
    kson_value = a.kson_value()
    
    if kson_value is None:
        # Si hay errores de parseo
        errors = a.errors()
        error_messages = '\n'.join([f"Error: {err.message()}" for err in errors])
        raise ValueError(f"Failed to parse Kson:\n{error_messages}")
    
    toml_string = kson_to_toml_string(kson_value)
    
    return toml_string