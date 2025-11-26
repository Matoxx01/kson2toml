import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from kson2toml.kson2toml import kson2toml
import toml

# All tests

def alltests():
    """
    All tests function
    - TomlString
    - TomlInteger
    - TomlFloat
    - TomlBoolean
    - TomlNull
    - TomlArray
    - TomlTable
    - TomlEmbed
    """
    # All implement
    pass

if __name__ == "__main__":
    alltests()

# Simple test

def kson_totoml_validation():
    """
    Testea la conversión de un archivo Kson a un string Toml
    """

    kson_file = Path(__file__).parent / 'fibonacci_sequence.kson'
    with open(kson_file, 'r') as f:
        kson_string = f.read()

    result = kson2toml(kson_string)
    print("Resultado de la conversión:")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Validar que el TOML sea válido
    try:
        parsed_toml = toml.loads(result)
        print("✓ El TOML generado es válido")
        print(f"Contenido parseado: {parsed_toml}")
        return True
    except toml.TomlDecodeError as e:
        print("✗ El TOML generado NO es válido")
        print(f"Errores encontrados:")
        print(f"  - {e}")
        return False
    except Exception as e:
        print("✗ Error inesperado al validar el TOML")
        print(f"  - {type(e).__name__}: {e}")
        return False