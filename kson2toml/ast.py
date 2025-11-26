"""
AST (Abstract Syntax Tree) para la conversión de KsonValue a TOML string.

Este módulo contiene las clases que representan los nodos del árbol de sintaxis
abstracta para poder convertir un KsonValue parseado a formato TOML.
"""
from kson import KsonValue, KsonValueType
from typing import Any, Dict, List


class TomlNode:
    """Clase base para todos los nodos del AST de TOML"""
    
    def to_toml(self, indent_level=0) -> str:
        """Convierte el nodo a string TOML"""
        raise NotImplementedError


class TomlString(TomlNode):
    """Representa un string en TOML"""
    
    def __init__(self, value: str):
        self.value = value
    
    def to_toml(self, indent_level=0) -> str:
        # Escapar caracteres especiales si es necesario
        if '\n' in self.value or '"' in self.value:
            # String multilínea
            return f'"""{self.value}"""'
        return f'"{self.value}"'


class TomlInteger(TomlNode):
    """Representa un entero en TOML"""
    
    def __init__(self, value: int):
        self.value = value
    
    def to_toml(self, indent_level=0) -> str:
        return str(self.value)


class TomlFloat(TomlNode):
    """Representa un float/decimal en TOML"""
    
    def __init__(self, value: float):
        self.value = value
    
    def to_toml(self, indent_level=0) -> str:
        return str(self.value)


class TomlBoolean(TomlNode):
    """Representa un booleano en TOML"""
    
    def __init__(self, value: bool):
        self.value = value
    
    def to_toml(self, indent_level=0) -> str:
        return 'true' if self.value else 'false'


class TomlNull(TomlNode):
    """Representa null en TOML (no existe nativamente, se convierte a string vacío o se omite)"""
    
    def to_toml(self, indent_level=0) -> str:
        # TOML no tiene null, retornamos string vacío
        return '""'


class TomlArray(TomlNode):
    """Representa un array en TOML"""
    
    def __init__(self, elements: List[TomlNode]):
        self.elements = elements
    
    def to_toml(self, indent_level=0) -> str:
        if not self.elements:
            return '[]'
        
        # Array en una línea para valores simples
        elements_str = ', '.join(elem.to_toml(indent_level) for elem in self.elements)
        return f'[{elements_str}]'


class TomlTable(TomlNode):
    """Representa una tabla/objeto en TOML"""
    
    def __init__(self, properties: Dict[str, TomlNode]):
        self.properties = properties
    
    def to_toml(self, indent_level=0, table_path='') -> str:
        """
        Convierte la tabla a TOML
        :param indent_level: Nivel de indentación
        :param table_path: Path de la tabla (ej: 'person' o 'person.address')
        """
        lines = []
        indent = '  ' * indent_level
        
        # Valores simples primero (key = value)
        for key, value in self.properties.items():
            if not isinstance(value, TomlTable):
                lines.append(f'{indent}{key} = {value.to_toml(indent_level)}')
        
        # Tablas anidadas después (como [table])
        for key, value in self.properties.items():
            if isinstance(value, TomlTable):
                full_path = f'{table_path}.{key}' if table_path else key
                lines.append('')  # Línea vacía antes de tabla
                lines.append(f'{indent}[{full_path}]')
                lines.append(value.to_toml(indent_level, full_path))
        
        return '\n'.join(lines)


class TomlEmbed(TomlNode):
    """Representa un embed block de Kson (contenido embebido como código)"""
    
    def __init__(self, content: str, tag: str = None, metadata: str = None):
        self.content = content
        self.tag = tag
        self.metadata = metadata
    
    def to_toml(self, indent_level=0) -> str:
        # En TOML, lo convertimos a string multilínea con comentario del tag
        result = f'"""\n{self.content}\n"""'
        if self.tag:
            result = f'# Tag: {self.tag}\n{result}'
        return result

# ----------------------------------------------------------
# Funciones generales para convertir KsonValue a TomlNode
# ----------------------------------------------------------

def kson_value_to_ast(kson_value: KsonValue) -> TomlNode:
    """
    Convierte un KsonValue a un nodo AST de TOML
    
    :param kson_value: El valor parseado de Kson
    :return: Un nodo TomlNode correspondiente
    """
    value_type = kson_value.value_type()
    
    if value_type == KsonValueType.STRING:
        return TomlString(kson_value.value())
    
    elif value_type == KsonValueType.INTEGER:
        return TomlInteger(kson_value.value())
    
    elif value_type == KsonValueType.DECIMAL:
        return TomlFloat(kson_value.value())
    
    elif value_type == KsonValueType.BOOLEAN:
        return TomlBoolean(kson_value.value())
    
    elif value_type == KsonValueType.NULL:
        return TomlNull()
    
    elif value_type == KsonValueType.ARRAY:
        elements = [kson_value_to_ast(elem) for elem in kson_value.elements()]
        return TomlArray(elements)
    
    elif value_type == KsonValueType.OBJECT:
        properties = {}
        for key, value in kson_value.properties().items():
            properties[key] = kson_value_to_ast(value)
        return TomlTable(properties)
    
    elif value_type == KsonValueType.EMBED:
        return TomlEmbed(
            content=kson_value.content(),
            tag=kson_value.tag(),
            metadata=kson_value.metadata()
        )
    
    else:
        raise ValueError(f"Tipo de valor Kson no soportado: {value_type}")


def kson_to_toml_string(kson_value: KsonValue) -> str:
    """
    Convierte un KsonValue completo a string TOML
    
    :param kson_value: El valor parseado de Kson
    :return: String en formato TOML
    """
    ast_node = kson_value_to_ast(kson_value)
    return ast_node.to_toml()