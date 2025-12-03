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
        # Para TOML, necesitamos escapar:
        # 1. Backslashes: \ -> \\
        # 2. Comillas dobles: " -> \"
        # 3. Newlines reales: \n (char 10) -> \\n
        
        # Primero verificar si hay newlines REALES (char 10)
        has_real_newlines = '\n' in self.value
        
        # Solo usar multi-line strings para strings con newlines Y otro contenido
        # Strings que son solo newlines o muy cortos deben usar formato normal
        if has_real_newlines and '"' not in self.value and len(self.value.strip()) > 0:
            # Usar multi-line string para newlines reales sin comillas
            # En multi-line, los backslashes no necesitan escape
            # Mantener el contenido exactamente como está
            return f'"""{self.value}"""'
        
        # Para strings normales, escapar en el orden correcto
        # 1. Primero backslashes (más importante, debe ser primero)
        escaped = self.value.replace('\\', '\\\\')
        
        # 2. Luego comillas dobles
        escaped = escaped.replace('"', '\\"')
        
        # 3. Si hay newlines reales, escaparlos también
        if '\n' in escaped:
            escaped = escaped.replace('\n', '\\n')
        
        return f'"{escaped}"'


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
    """Representa null en TOML (no existe nativamente, se convierte a string)"""
    
    def to_toml(self, indent_level=0) -> str:
        # TOML no tiene null, retornamos "null" como string
        return '"null"'


class TomlArray(TomlNode):
    """Representa un array en TOML"""
    
    def __init__(self, elements: List[TomlNode]):
        self.elements = elements
        self.is_heterogeneous = False
    
    def check_heterogeneous(self) -> bool:
        """
        Verifica si el array necesita ser convertido a array of tables.
        TOML puede representar arrays heterogéneos usando inline tables,
        pero NO puede representar arrays de primitivos mezclados sin tablas.
        
        Retorna True solo cuando hay primitivos puros mezclados SIN tablas.
        """
        if not self.elements:
            return False
        
        # Categorizar elementos
        has_table = False
        has_array = False
        primitive_types = set()
        
        for elem in self.elements:
            if isinstance(elem, TomlTable):
                has_table = True
            elif isinstance(elem, TomlArray):
                has_array = True
            elif isinstance(elem, (TomlString, TomlInteger, TomlFloat, TomlBoolean, TomlNull)):
                # Clasificar primitivos
                if isinstance(elem, TomlString):
                    primitive_types.add('string')
                elif isinstance(elem, (TomlInteger, TomlFloat)):
                    primitive_types.add('number')  # Integers y floats se consideran compatibles
                elif isinstance(elem, TomlBoolean):
                    primitive_types.add('boolean')
                elif isinstance(elem, TomlNull):
                    primitive_types.add('null')
        
        # Si hay mezcla de arrays con primitivos, necesitamos array of tables
        if has_array and primitive_types:
            return True
        
        # Si hay tablas, TOML puede representarlo con inline tables
        # No es necesario array of tables
        if has_table:
            return False
        
        # Si solo hay primitivos y hay más de un tipo diferente, necesitamos array of tables
        return len(primitive_types) > 1
    
    def to_toml(self, indent_level=0) -> str:
        if not self.elements:
            return '[]'
        
        # Verificar si hay tablas (objetos)
        has_tables = any(isinstance(elem, TomlTable) for elem in self.elements)
        has_arrays = any(isinstance(elem, TomlArray) for elem in self.elements)
        
        if has_tables:
            # Array con tablas - usar inline table format
            elements_str = ', '.join(
                elem.to_inline() if isinstance(elem, TomlTable) else elem.to_toml(indent_level) 
                for elem in self.elements
            )
            return f'[{elements_str}]'
        elif has_arrays or len(self.elements) > 3:
            # Array multilínea con indentación
            indent = '    ' * indent_level
            next_indent = '    ' * (indent_level + 1)
            lines = ['[']
            for i, elem in enumerate(self.elements):
                elem_str = elem.to_toml(indent_level + 1)
                if i < len(self.elements) - 1:
                    lines.append(f'{next_indent}{elem_str},')
                else:
                    lines.append(f'{next_indent}{elem_str}')
            lines.append(f'{indent}]')
            return '\n'.join(lines)
        else:
            # Array en una línea para valores simples
            elements_str = ', '.join(elem.to_toml(indent_level) for elem in self.elements)
            return f'[{elements_str}]'


class TomlTable(TomlNode):
    """Representa una tabla/objeto en TOML"""
    
    def __init__(self, properties: Dict[str, TomlNode]):
        self.properties = properties
    
    def to_inline(self) -> str:
        """Convierte la tabla a formato inline {key = value}""" 
        items = []
        for key, value in self.properties.items():
            if ' ' in key or '-' in key or key in ['false', 'true', 'null']:
                key_str = f'"{key}"'
            else:
                key_str = key
            
            if isinstance(value, TomlArray):
                value_str = value.to_toml(0)
            else:
                value_str = value.to_toml(0)
            
            items.append(f'{key_str} = {value_str}')
        return '{' + ', '.join(items) + '}'
    
    def to_toml(self, indent_level=0, table_path='') -> str:
        """
        Convierte la tabla a TOML
        :param indent_level: Nivel de indentación
        :param table_path: Path de la tabla (ej: 'person' o 'person.address')
        """
        lines = []
        
        # Valores simples primero (key = value)
        simple_values = []
        nested_tables = []
        nested_arrays = []
        
        for key, value in self.properties.items():
            if isinstance(value, TomlTable):
                nested_tables.append((key, value))
            elif isinstance(value, TomlArray) and any(isinstance(elem, TomlTable) for elem in value.elements):
                # Array de tablas
                nested_arrays.append((key, value))
            else:
                simple_values.append((key, value))
        
        # Primero los valores simples
        for key, value in simple_values:
            # Manejar embeds especialmente cuando son propiedades
            if isinstance(value, TomlEmbed) and key != 'embedContent':
                # Embed como valor de propiedad - crear tabla anidada
                full_path = f'{table_path}.{key}' if table_path else key
                if lines:
                    lines.append('')
                lines.append(f'[{full_path}]')
                lines.append(f'embedContent = {value.to_toml(indent_level)}')
            else:
                value_str = value.to_toml(indent_level)
                # Escapar la key si contiene espacios o caracteres especiales
                if ' ' in key or '-' in key or key in ['false', 'true', 'null']:
                    lines.append(f'"{key}" = {value_str}')
                else:
                    lines.append(f'{key} = {value_str}')
        
        # Luego arrays de tablas
        for key, array in nested_arrays:
            for elem in array.elements:
                if isinstance(elem, TomlTable):
                    full_path = f'{table_path}.{key}' if table_path else key
                    if lines:  # Agregar línea vacía si no es el primero
                        lines.append('')
                    lines.append(f'[[{full_path}]]')
                    table_lines = elem.to_toml(0, full_path).split('\n')
                    lines.extend([line for line in table_lines if line.strip() and not line.strip().startswith('[')])
        
        # Finalmente las tablas anidadas
        for key, value in nested_tables:
            full_path = f'{table_path}.{key}' if table_path else key
            if lines:  # Agregar línea vacía si no es el primero
                lines.append('')
            lines.append(f'[{full_path}]')
            lines.append(value.to_toml(0, full_path))
        
        return '\n'.join(lines)


class TomlEmbed(TomlNode):
    """Representa un embed block de Kson (contenido embebido como código)"""
    
    def __init__(self, content: str, tag: str = None, metadata: str = None):
        self.content = content
        self.tag = tag
        self.metadata = metadata
    
    def to_toml(self, indent_level=0) -> str:
        # En TOML, lo convertimos a string multilínea
        # NO eliminar whitespace - preservar el contenido exacto del embed block
        content = self.content
        
        # Escapar backslashes en multi-line strings para TOML
        # En TOML multi-line strings, backslash seguido de ciertos chars es escape sequence
        # Necesitamos duplicar backslashes para preservarlos literalmente
        content = content.replace('\\', '\\\\')
        
        # Si el contenido no termina con newline, agregar uno
        if not content.endswith('\n'):
            content = content + '\n'
        
        return f'"""\n{content}"""'

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
    
    # Si el valor raíz no es una tabla (objeto), envolver con 'value ='
    if not isinstance(ast_node, TomlTable):
        # Especial: si es un embed con tag, crear tabla
        if isinstance(ast_node, TomlEmbed) and (ast_node.tag or ast_node.metadata):
            # Usar tag si existe, sino usar metadata
            tag_value = ast_node.tag if ast_node.tag else ast_node.metadata
            # Crear una tabla con embedTag y embedContent
            embed_table = TomlTable({'embedTag': TomlString(tag_value), 'embedContent': ast_node})
            # Necesitamos envolver en [embedBlock]
            return '[embedBlock]\n' + embed_table.to_toml()
        elif isinstance(ast_node, TomlEmbed):
            # Embed sin tag, usar solo embedContent
            return f'embedContent = {ast_node.to_toml()}'
        elif isinstance(ast_node, TomlArray) and ast_node.check_heterogeneous():
            # Array heterogéneo - convertir a array of tables
            lines = []
            for elem in ast_node.elements:
                lines.append('[[value]]')
                if isinstance(elem, TomlTable):
                    # Si es tabla, agregar sus propiedades directamente
                    lines.append(elem.to_toml())
                else:
                    # Si es valor simple, agregarlo como 'item'
                    lines.append(f'item = {elem.to_toml()}')
                lines.append('')  # Línea vacía entre elementos
            return '\n'.join(lines).rstrip()  # Eliminar última línea vacía
        else:
            return f'value = {ast_node.to_toml()}'
    else:
        return ast_node.to_toml()