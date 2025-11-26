"""
Documentation for the Kson2toml converter.
"""
from kson import Kson
from kson2toml.ast import kson_to_toml_string

def kson2toml(kson_string):
    """
    Lógica de conversión de Kson a Toml
    
    :param kson_string: La cadena completa en formato Kson

    :return toml_string: Conversión completa a cadena Toml
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