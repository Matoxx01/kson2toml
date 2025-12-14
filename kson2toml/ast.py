"""
AST (Abstract Syntax Tree) para la conversión de KsonValue a TOML string.

Este módulo contiene las clases que representan los nodos del árbol de sintaxis
abstracta para poder convertir un KsonValue parseado a formato TOML.
"""
from kson import KsonValue, KsonValueType
from typing import Any, Dict, List
import textwrap


class TomlNode:
    """Clase base para todos los nodos del AST de TOML"""
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        """Convierte el nodo a string TOML"""
        raise NotImplementedError


class TomlString(TomlNode):
    """Representa un string en TOML"""
    
    def __init__(self, value: str, allow_multiline: bool = True):
        # Procesar escapes KSON: $ seguido de whitespace
        # En KSON, $ indica que el whitespace que sigue debe preservarse literalmente
        # Basado en los tests, $ + espacio/whitespace se convierte a TAB en el output
        value = value.replace('$ ', '\t')  # $ + espacio -> tab
        value = value.replace('$\t', '\t')  # $ + tab -> tab (ya es tab)
        # Y otros escapes de whitespace que puedan haber
        self.value = value
        self.allow_multiline = allow_multiline
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        # Para TOML, hay dos tipos de strings:
        # - Single quotes '...': literales, no escapan nada (excepto que no pueden contener ')
        # - Double quotes "...": escapan backslashes y comillas
        # - Triple quotes """...""": multi-línea, permiten newlines y tabs reales
        
        # Primero verificar si hay newlines REALES (char 10) o tabs
        has_real_newlines = '\n' in self.value
        has_real_tabs = '\t' in self.value
        
        # Usar multi-line strings para strings con newlines o tabs reales SOLO si está permitido
        # Multi-line strings preservan whitespace literal sin escape
        if self.allow_multiline and (has_real_newlines or has_real_tabs) and len(self.value.strip()) > 0:
            # En multi-line, los backslashes y comillas no necesitan escape
            # Mantener el contenido exactamente como está
            return f'"""{self.value}"""'
        
        # Decidir entre single y double quotes para strings de una línea
        # Usar single quotes cuando hay backslashes Y comillas dobles, Y NO hay single quotes
        # En TOML literal strings (single-quoted), los backslashes AÚN necesitan escaparse como \\
        # pero las comillas dobles NO necesitan escape
        has_single_quote = "'" in self.value
        has_backslash = '\\' in self.value
        has_double_quote = '"' in self.value
        
        if has_backslash and has_double_quote and not has_single_quote:
            # Usar single quotes: comillas dobles no necesitan escape, pero backslashes sí
            escaped = self.value.replace('\\', '\\\\')
            return f"'{escaped}'"
        
        # Usar double quotes por defecto
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
    
    def __init__(self, value: int, literal: str = None):
        self.value = value
        self.literal = literal  # Texto literal del source
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        # Usar literal si está disponible, sino convertir el valor
        return self.literal if self.literal else str(self.value)


class TomlFloat(TomlNode):
    """Representa un float/decimal en TOML"""
    
    def __init__(self, value: float, literal: str = None):
        self.value = value
        self.literal = literal  # Texto literal del source
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        # Usar literal si está disponible, sino convertir el valor
        return self.literal if self.literal else str(self.value)


class TomlBoolean(TomlNode):
    """Representa un booleano en TOML"""
    
    def __init__(self, value: bool):
        self.value = value
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        return 'true' if self.value else 'false'


class TomlNull(TomlNode):
    """Representa null en TOML (no existe nativamente, se convierte a string)"""
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        # TOML no tiene null, retornamos "null" como string
        return '"null"'


class TomlArray(TomlNode):
    """Representa un array en TOML"""
    
    def __init__(self, elements: List[TomlNode], start_line: int = None, end_line: int = None):
        self.elements = elements
        self.is_heterogeneous = False
        self.start_line = start_line  # Línea inicial en el source KSON
        self.end_line = end_line      # Línea final en el source KSON
    
    def check_heterogeneous(self) -> bool:
        """
        Verifica si el array necesita ser convertido a array of tables.
        
        Solo retorna True para casos muy específicos que no pueden usar inline tables:
        - Arrays que mezclan arrays-con-objetos con primitivos/strings
        
        La mayoría de arrays (incluso con objetos) pueden usar inline tables.
        
        Retorna True cuando el array necesita formato array of tables [[...]].
        """
        if not self.elements:
            return False
        
        # Verificar si hay arrays que contienen objetos mezclados con otros tipos
        has_array_with_tables = False
        has_other_types = False
        
        for elem in self.elements:
            if isinstance(elem, TomlArray):
                # Verificar si este array contiene tablas
                if any(isinstance(e, TomlTable) for e in elem.elements):
                    has_array_with_tables = True
                else:
                    # Array sin tablas cuenta como "otro tipo"
                    has_other_types = True
            elif isinstance(elem, TomlTable):
                # Tablas directas NO necesitan array of tables, pueden usar inline
                has_other_types = True
            else:
                # Primitivos
                has_other_types = True
        
        # Solo usar array of tables si hay arrays-con-tablas mezclados con otros tipos
        return has_array_with_tables and has_other_types
    
    def needs_array_of_tables_format(self) -> bool:
        """
        Determina si este array (como valor raíz) debe usar formato array of tables.
        
        En TOML, ciertos arrays heterogéneos necesitan array-of-tables:
        - Mezcla de array + primitivos (array + booleano, array + número, etc)
        - Múltiples tipos primitivos diferentes (string + número, booleano + null, etc)
        
        Lo que NO necesita array-of-tables:
        - Array + string simple (ambos son valores válidos en array)
        
        Ejemplos que necesitan array of tables:
        - [true, false, [1.2]] -> booleano + array
        - [1, "string"] -> número + string (tipos primitivos diferentes)
        - [true, false, null] -> 3 tipos primitivos
        
        Ejemplos que NO necesitan:
        - [["a", "b"], "c"] -> array + string (representable como array simple)
        - [[1, 2], [3, 4]] -> solo arrays
        - [1, 2, 3] -> un solo tipo primitivo
        """
        if not self.elements:
            return False
        
        # Contar tipos
        has_string = False
        has_number = False
        has_boolean = False
        has_null = False
        has_array = False
        has_table = False
        
        for elem in self.elements:
            if isinstance(elem, TomlString):
                has_string = True
            elif isinstance(elem, (TomlInteger, TomlFloat)):
                has_number = True
            elif isinstance(elem, TomlBoolean):
                has_boolean = True
            elif isinstance(elem, TomlNull):
                has_null = True
            elif isinstance(elem, TomlArray):
                has_array = True
            elif isinstance(elem, TomlTable):
                has_table = True
        
        # Si hay array + algo que NO sea string → usar array of tables
        # (array + primitivo, o array + tabla)
        if has_array and (has_number or has_boolean or has_null or has_table):
            return True
        
        # Contar cuántos tipos PRIMITIVOS diferentes hay (sin arrays ni tablas)
        primitive_types_count = sum([has_string, has_number, has_boolean, has_null])
        
        # Si hay 2+ tipos primitivos diferentes → usar array of tables
        if primitive_types_count >= 2:
            return True
        
        # Otros casos → array estándar
        return False
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        if comments is None:
            comments = {}
        
        if not self.elements:
            return '[]'
        
        # Verificar si hay tablas (objetos)
        has_tables = any(isinstance(elem, TomlTable) for elem in self.elements)
        has_arrays = any(isinstance(elem, TomlArray) for elem in self.elements)
        has_comments = bool(comments)
        
        if has_tables:
            # Array con tablas - usar inline table format
            elements_str = ', '.join(
                elem.to_inline() if isinstance(elem, TomlTable) else elem.to_toml(indent_level, {}, source) 
                for elem in self.elements
            )
            return f'[{elements_str}]'
        elif has_arrays or len(self.elements) > 3 or has_comments:
            # Array multilínea con indentación - insertar comentarios antes de cada elemento
            indent = '    ' * indent_level
            next_indent = '    ' * (indent_level + 1)
            lines = ['[']
            
            # Si hay comentarios inline, distribuirlos entre los elementos
            if source and comments:
                # Para arrays, necesitamos distribuir comentarios correctamente
                # Cada grupo de comentarios va antes del elemento correspondiente
                # Si hay más grupos de comentarios que elementos, algunos se agregan al final
                
                # Obtener todos los grupos de comentarios en orden
                sorted_comment_lines = sorted(comments.keys())
                
                # Si SOLO hay comentarios -1 (leading), usar formato compacto sin indent
                # Esto solo aplica cuando NO hay inline comments (comentarios entre elementos)
                compact_mode = len(sorted_comment_lines) == 1 and sorted_comment_lines[0] == -1
                elem_indent = indent if compact_mode else next_indent
                
                # Distribuir: un grupo de comentarios por elemento
                # Rastrear qué comentarios han sido consumidos por arrays anidados
                consumed_comment_lines = set()
                
                # Distribuir: un grupo de comentarios por elemento
                for i, elem in enumerate(self.elements):
                    # Si el elemento es un array anidado, pasar comentarios que caen en su rango
                    elem_comments = {}
                    if isinstance(elem, TomlArray) and elem.start_line is not None and elem.end_line is not None:
                        for comment_line, comment_list in comments.items():
                            if comment_line >= 0 and elem.start_line <= comment_line <= elem.end_line:
                                elem_comments[comment_line] = comment_list
                                consumed_comment_lines.add(comment_line)
                    
                    # Agregar el grupo de comentarios correspondiente a este elemento (si no fue consumido)
                    if i < len(sorted_comment_lines):
                        line_num = sorted_comment_lines[i]
                        if line_num not in consumed_comment_lines:
                            # Comentarios -1: en modo compacto sin indent, sino depende de si hay inline
                            if line_num == -1:
                                # Leading comments en modo compacto: sin indent
                                # Leading comments en modo normal (hay inline): con indent normal
                                comment_indent = indent if compact_mode else next_indent
                            else:
                                # Inline comments siempre con next_indent
                                comment_indent = next_indent
                            for comment in comments[line_num]:
                                lines.append(f'{comment_indent}{comment}')
                    
                    elem_str = elem.to_toml(indent_level + 1 if not compact_mode else indent_level, elem_comments, source)
                    if i < len(self.elements) - 1:
                        lines.append(f'{elem_indent}{elem_str},')
                    else:
                        lines.append(f'{elem_indent}{elem_str}')
                
                # Si hay comentarios extras después del último elemento, agregarlos (si no fueron consumidos)
                if len(sorted_comment_lines) > len(self.elements):
                    for i in range(len(self.elements), len(sorted_comment_lines)):
                        line_num = sorted_comment_lines[i]
                        if line_num not in consumed_comment_lines:
                            for comment in comments[line_num]:
                                lines.append(f'{next_indent}{comment}')
            else:
                for i, elem in enumerate(self.elements):
                    elem_str = elem.to_toml(indent_level + 1, {}, source)
                    if i < len(self.elements) - 1:
                        lines.append(f'{next_indent}{elem_str},')
                    else:
                        lines.append(f'{next_indent}{elem_str}')
            
            lines.append(f'{indent}]')
            return '\n'.join(lines)
        else:
            # Array en una línea para valores simples sin comentarios
            elements_str = ', '.join(elem.to_toml(indent_level, {}, source) for elem in self.elements)
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
    
    def to_toml(self, indent_level=0, table_path='', comments=None, source=None) -> str:
        """
        Convierte la tabla a TOML
        :param indent_level: Nivel de indentación
        :param table_path: Path de la tabla (ej: 'person' o 'person.address')
        :param comments: Dict de comentarios inline {line_num: [comment_texts]}
                        Nota: line_num es la línea en el source KSON donde aparece la propiedad
        :param source: El código fuente Kson original
        """
        if comments is None:
            comments = {}
        
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
        
        # Mapear comentarios a propiedades basado en source
        property_comments = {k: [] for k, v in simple_values}
        
        if source and comments and simple_values:
            source_lines = source.split('\n')
            
            # Encontrar línea de cada propiedad en el source
            key_line = {}
            for line_num, line in enumerate(source_lines):
                stripped = line.strip()
                if ':' in stripped and not stripped.startswith('#'):
                    key_part = stripped.split(':', 1)[0].strip()
                    if key_part.startswith('"') and key_part.endswith('"'):
                        key_part = key_part[1:-1]
                    # Buscar en simple_values
                    for k, v in simple_values:
                        if k == key_part:
                            key_line[k] = line_num
            
            # Asignar comentarios a propiedades
            # comments tiene {line_num: [comentarios]}  donde line_num es la línea de la propiedad
            for line_num, comment_list in comments.items():
                # Buscar qué propiedad está en esta línea
                for k, k_line in key_line.items():
                    if k_line == line_num:
                        property_comments[k].extend(comment_list)
        
        # Primero los valores simples con sus comentarios
        # Obtener keys de las tablas anidadas para decidir si escapar propiedades
        nested_tables_keys = {k for k, v in nested_tables}
        
        for key, value in simple_values:
            # Agregar comentarios para esta propiedad
            for comment_text in property_comments[key]:
                lines.append(comment_text)
            
            # Manejar embeds especialmente cuando son propiedades
            if isinstance(value, TomlEmbed) and key != 'embedContent':
                # Embed como valor de propiedad - crear tabla anidada
                full_path = f'{table_path}.{key}' if table_path else key
                if lines:
                    lines.append('')
                lines.append(f'[{full_path}]')
                lines.append(f'embedContent = {value.to_toml(indent_level, {}, source)}')
            else:
                # Si es embedContent pero una string normal (no embed), no usar multiline
                if key == 'embedContent' and isinstance(value, TomlString):
                    # Desabilitar multiline para embedContent que es string simple
                    value.allow_multiline = False
                    value_str = value.to_toml(indent_level, {}, source)
                    value.allow_multiline = True  # Restaurar por si acaso
                else:
                    value_str = value.to_toml(indent_level, {}, source)
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
                    table_lines = elem.to_toml(0, full_path, {}, source).split('\n')
                    lines.extend([line for line in table_lines if line.strip() and not line.strip().startswith('[')])
        
        # Finalmente las tablas anidadas
        for key, value in nested_tables:
            full_path = f'{table_path}.{key}' if table_path else key
            if lines:  # Agregar línea vacía si no es el primero
                lines.append('')
            lines.append(f'[{full_path}]')
            lines.append(value.to_toml(0, full_path, {}, source))
        
        return '\n'.join(lines)


class TomlEmbed(TomlNode):
    """Representa un embed block de Kson (contenido embebido como código)"""
    
    def __init__(self, content: str, tag: str = None, metadata: str = None, has_escapes: bool = False):
        self.content = content
        self.tag = tag
        self.metadata = metadata
        self.has_escapes = has_escapes
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        # En TOML, lo convertimos a string
        content = self.content
        
        # Si NO tiene escapes, hacer dedent normal
        if not self.has_escapes:
            content = textwrap.dedent(content)
        
        # Si el contenido no termina con newline, agregar uno
        if not content.endswith('\n'):
            content = content + '\n'
        
        # En TOML triple-quoted strings, los escapes se procesan
        # Siempre escapar backslashes para evitar errores de parseo (ej: \ -> \\)
        # Esto previene secuencias de escape inválidas
        content = content.replace('\\', '\\\\')
        
        # Siempre usar triple-quoted para embeds (para preservar exacto formato)
        return f'"""\n{content}"""'

# ----------------------------------------------------------
# Funciones generales para convertir KsonValue a TomlNode
# ----------------------------------------------------------

def extract_literal_text(kson_value, tokens, source):
    """
    Extrae el texto literal de un valor desde el source original.
    Útil para preservar el formato exacto de números (notación científica, etc).
    
    :param kson_value: El KsonValue
    :param tokens: Lista de tokens del análisis
    :param source: El código fuente Kson original
    :return: String con el texto literal o None si no se puede extraer
    """
    if tokens is None or source is None:
        return None
    
    try:
        # Buscar el token que corresponde a este valor
        # Usamos start() y end() del KsonValue para encontrar la posición
        start_pos = kson_value.start()
        end_pos = kson_value.end()
        
        start_line = start_pos.line()
        start_col = start_pos.column()
        end_line = end_pos.line()
        end_col = end_pos.column()
        
        lines = source.split('\n')
        
        if start_line == end_line:
            # Mismo línea
            return lines[start_line][start_col:end_col]
        else:
            # Múltiples líneas
            result_lines = []
            for line_num in range(start_line, end_line + 1):
                line = lines[line_num]
                if line_num == start_line:
                    result_lines.append(line[start_col:])
                elif line_num == end_line:
                    result_lines.append(line[:end_col])
                else:
                    result_lines.append(line)
            return '\n'.join(result_lines)
    except (AttributeError, IndexError, Exception):
        return None


def extract_raw_embed_content(kson_value, tokens, source):
    """
    Extrae el contenido del embed.
    KSON retorna el contenido con escapes literales (ej: %\% no es convertido a %).
    Necesitamos convertir estos escapes al formato TOML apropiado.
    
    Sin embargo, si el contenido es un "embed complejo" que contiene estructura KSON
    (otros embeds, propiedades con :, etc.), los escapes NO deben convertirse.
    
    :param kson_value: El KsonValue de tipo EMBED
    :param tokens: Lista de tokens del análisis (no usado)
    :param source: El código fuente Kson original (no usado)
    :return: Tupla (content, has_escapes)
    """
    # Usar el contenido procesado por KSON
    content = kson_value.content()
    
    # Detectar si hay escapes o backslashes en el contenido
    has_escapes = '%\\%' in content or '$\\$' in content or '\\' in content
    
    if '%\\%' in content or '$\\$' in content:
        # Detectar si el contenido es "complejo" (contiene estructura KSON)
        # Indicadores de contenido complejo:
        # - Contiene ":\n" (propiedades KSON)
        # - Contiene " $\n" o " %\n" (otros embeds)
        # - Contiene líneas que parecen claves KSON
        has_kson_structure = (
            ':\n' in content or
            ':\r' in content or
            ': ' in content or
            '\n$' in content or
            '\n%' in content
        )
        
        if not has_kson_structure:
            # Es contenido simple, convertir escapes: %\% -> %%  y  $\$ -> $$
            content = content.replace('%\\%', '%%').replace('$\\$', '$$')
            # Marcar que NO tiene escapes ahora (ya fueron procesados)
            has_escapes = False
    
    return content, has_escapes




def extract_comments_with_mapping(kson_string, tokens):
    """
    Extrae los comentarios del código fuente Kson y los mapea a los tokens.
    Retorna información detallada sobre dónde colocar cada comentario.
    
    :param kson_string: El código fuente Kson
    :param tokens: Lista de tokens del análisis
    :return: Dict con 'leading', 'inline', 'trailing'
    """
    lines = kson_string.split('\n')
    
    # Obtener líneas con tokens reales (no EOF)
    token_lines = []
    for token in tokens:
        if token.text() and token.text().strip():
            token_lines.append(token.start().line())
    
    # Clasificar comentarios
    leading_comments = []  # Comentarios antes del primer token
    inline_comments = {}  # Comentarios entre tokens: {line_del_siguiente_token: [comentarios]}
    trailing_comments = []  # Comentarios después del último token
    
    first_token_line = token_lines[0] if token_lines else None
    last_token_line = token_lines[-1] if token_lines else None
    
    pending_comments = []
    found_first_content = False
    
    for line_num, line in enumerate(lines):
        stripped = line.strip()
        
        # Detectar comentarios inline (mismo renglón que el código)
        if '#' in stripped and not stripped.startswith('#'):
            # Hay un comentario inline en esta línea con contenido
            parts = stripped.split('#', 1)
            if len(parts) == 2:
                # Preservar el espacio después de # si existe
                comment_text = parts[1]
                if comment_text.startswith(' '):
                    comment = '# ' + comment_text[1:]
                else:
                    comment = '#' + comment_text
                # Comentario inline se trata como leading si no hay otro contenido
                if not found_first_content:
                    leading_comments.append(comment)
                    found_first_content = True
                else:
                    # Asociar con la siguiente línea de contenido
                    if line_num + 1 not in inline_comments:
                        inline_comments[line_num + 1] = []
                    inline_comments[line_num + 1].append(comment)
        elif stripped.startswith('#'):
            pending_comments.append(stripped)
        elif stripped:  # Línea con contenido no comentario
            # Esta es una línea con token
            if not found_first_content:
                # Primeros comentarios encontrados antes del primer contenido
                if pending_comments:
                    leading_comments.extend(pending_comments)
                    pending_comments = []
                found_first_content = True
            else:
                # Comentarios inline - asociar con esta línea de token
                if pending_comments:
                    inline_comments[line_num] = pending_comments.copy()
                    pending_comments = []
    
    # Comentarios finales que quedaron
    if pending_comments:
        if not found_first_content:
            leading_comments.extend(pending_comments)
        else:
            trailing_comments.extend(pending_comments)
    
    return {
        'leading': leading_comments,
        'inline': inline_comments,
        'trailing': trailing_comments,
        'lines': lines
    }


def kson_value_to_ast(kson_value: KsonValue, tokens: List = None, source: str = None) -> TomlNode:
    """
    Convierte un KsonValue a un nodo AST de TOML
    
    :param kson_value: El valor parseado de Kson
    :param tokens: Lista de tokens del análisis (para obtener raw content de embeds)
    :param source: El código fuente Kson original (para obtener raw content de embeds)
    :return: Un nodo TomlNode correspondiente
    """
    value_type = kson_value.value_type()
    
    if value_type == KsonValueType.STRING:
        return TomlString(kson_value.value())
    
    elif value_type == KsonValueType.INTEGER:
        # Extraer texto literal para preservar formato
        literal = extract_literal_text(kson_value, tokens, source)
        return TomlInteger(kson_value.value(), literal)
    
    elif value_type == KsonValueType.DECIMAL:
        # Extraer texto literal para preservar notación científica
        literal = extract_literal_text(kson_value, tokens, source)
        return TomlFloat(kson_value.value(), literal)
    
    elif value_type == KsonValueType.BOOLEAN:
        return TomlBoolean(kson_value.value())
    
    elif value_type == KsonValueType.NULL:
        return TomlNull()
    
    elif value_type == KsonValueType.ARRAY:
        elements = [kson_value_to_ast(elem, tokens, source) for elem in kson_value.elements()]
        # Capturar información de posición del array
        start_line = kson_value.start().line() if kson_value.start() else None
        end_line = kson_value.end().line() if kson_value.end() else None
        return TomlArray(elements, start_line=start_line, end_line=end_line)
    
    elif value_type == KsonValueType.OBJECT:
        properties = {}
        for key, value in kson_value.properties().items():
            properties[key] = kson_value_to_ast(value, tokens, source)
        return TomlTable(properties)
    
    elif value_type == KsonValueType.EMBED:
        # Extraer el contenido del embed (con o sin delimitadores según escapes)
        content, has_escapes = extract_raw_embed_content(kson_value, tokens, source)
        
        return TomlEmbed(
            content=content,
            tag=kson_value.tag(),
            metadata=kson_value.metadata(),
            has_escapes=has_escapes
        )
    
    else:
        raise ValueError(f"Tipo de valor Kson no soportado: {value_type}")


def kson_to_toml_string(kson_value: KsonValue, comment_map: Dict = None, source: str = None, tokens: List = None) -> str:
    """
    Convierte un KsonValue completo a string TOML con comentarios preservados
    
    :param kson_value: El valor parseado de Kson
    :param comment_map: Dict con 'leading', 'inline', 'trailing' comments
    :param source: El código fuente Kson original
    :param tokens: Lista de tokens del análisis (para procesamiento de embeds)
    :return: String en formato TOML
    """
    if comment_map is None:
        comment_map = {'leading': [], 'inline': {}, 'trailing': []}
    
    ast_node = kson_value_to_ast(kson_value, tokens, source)
    
    leading_comments = comment_map.get('leading', [])
    inline_comments = comment_map.get('inline', {})
    trailing_comments = comment_map.get('trailing', [])
    
    result_lines = []
    
    # Si el valor raíz no es una tabla (objeto), envolver con 'value ='
    if not isinstance(ast_node, TomlTable):
        # Arrays heterogéneos (tipos mezclados) deben usar formato array of tables
        if isinstance(ast_node, TomlArray) and ast_node.needs_array_of_tables_format():
            # Generar formato [[value]] con item = ...
            if leading_comments:
                result_lines.extend(leading_comments)
            
            for elem in ast_node.elements:
                result_lines.append('[[value]]')
                result_lines.append(f'item = {elem.to_toml()}')
                result_lines.append('')  # Línea en blanco entre elementos
            
            # Remover la última línea en blanco si existe
            if result_lines and result_lines[-1] == '':
                result_lines.pop()
        
        # Para arrays, decidir si los leading comments van antes o dentro del array
        # Lógica:
        # - Si hay arrays anidados + inline_comments (2+): TODOS los leading van FUERA
        # - Si hay 2+ leading + inline_comments: todos menos el último van FUERA, el último va DENTRO
        # - Si hay 1-2 leading sin arrays anidados: TODOS van DENTRO
        elif isinstance(ast_node, TomlArray) and not ast_node.check_heterogeneous():
            # Verificar si el array contiene arrays anidados
            has_nested_arrays = any(isinstance(elem, TomlArray) for elem in ast_node.elements)
            
            # Determinar si los inline_comments son "generalizados" (2+ elementos con comentarios)
            inline_comment_count = len(inline_comments) if inline_comments else 0
            
            # Si hay ARRAYS ANIDADOS + inline_comments (2+), todos los leading van FUERA
            if leading_comments and has_nested_arrays and inline_comments and inline_comment_count >= 2:
                # Hay arrays anidados + comentarios en múltiples elementos -> leading es general
                result_lines.extend(leading_comments)
                result_lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
            elif leading_comments and len(leading_comments) >= 2 and inline_comments:
                # 2+ leading + hay inline_comments: separar último del resto
                # El último leading va dentro (para el primer elemento), el resto fuera
                outer_leading = leading_comments[:-1]  # Todos menos el último
                inner_leading = [leading_comments[-1]]  # El último
                
                result_lines.extend(outer_leading)
                combined_comments = {-1: inner_leading}
                combined_comments.update(inline_comments)
                result_lines.append(f'value = {ast_node.to_toml(comments=combined_comments, source=source)}')
            elif leading_comments:
                # 1 leading, o leading sin inline: todos DENTRO (modo compacto)
                combined_comments = {-1: leading_comments}
                if inline_comments:
                    combined_comments.update(inline_comments)
                result_lines.append(f'value = {ast_node.to_toml(comments=combined_comments, source=source)}')
            else:
                # Sin leading comments
                result_lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
        # Especial: si es un embed con tag, crear tabla
        elif isinstance(ast_node, TomlEmbed) and (ast_node.tag or ast_node.metadata):
            # Agregar comentarios iniciales
            if leading_comments:
                result_lines.extend(leading_comments)
            # Usar tag si existe, sino usar metadata
            tag_value = ast_node.tag if ast_node.tag else ast_node.metadata
            # Crear una tabla con embedTag y embedContent
            embed_table = TomlTable({'embedTag': TomlString(tag_value), 'embedContent': ast_node})
            # Necesitamos envolver en [embedBlock]
            result_lines.append('[embedBlock]')
            result_lines.append(embed_table.to_toml(comments=inline_comments, source=source))
        elif isinstance(ast_node, TomlEmbed):
            # Agregar comentarios iniciales
            if leading_comments:
                result_lines.extend(leading_comments)
                # Si hay comentarios, usar 'value =' en lugar de 'embedContent ='
                result_lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
            else:
                # Embed sin tag y sin comentarios, usar embedContent
                result_lines.append(f'embedContent = {ast_node.to_toml(comments=inline_comments, source=source)}')
        elif isinstance(ast_node, TomlArray) and ast_node.check_heterogeneous():
            # Agregar comentarios iniciales
            if leading_comments:
                result_lines.extend(leading_comments)
            # Array heterogéneo - convertir a array of tables
            lines = []
            # Determinar si hay cualquier array o tabla anidada
            has_arrays = any(isinstance(elem, TomlArray) for elem in ast_node.elements)
            has_tables = any(isinstance(elem, TomlTable) for elem in ast_node.elements)
            
            # Usar 'list_item' si hay arrays o tablas, sino usar 'item'
            key_name = 'list_item' if (has_arrays or has_tables) else 'item'
            
            for elem in ast_node.elements:
                lines.append('[[value]]')
                if isinstance(elem, TomlTable):
                    # Si es tabla, agregar sus propiedades directamente
                    lines.append(elem.to_toml(comments=inline_comments, source=source))
                elif isinstance(elem, TomlArray):
                    # Si es un array anidado, usar la clave determinada
                    # Verificar si el array contiene tablas para decidir sintaxis
                    has_inner_tables = any(isinstance(e, TomlTable) for e in elem.elements)
                    if has_inner_tables:
                        # Usar sintaxis [[value.list_item]] para arrays con tablas
                        for table_elem in elem.elements:
                            if isinstance(table_elem, TomlTable):
                                lines.append(f'[[value.{key_name}]]')
                                lines.append(table_elem.to_toml(comments=inline_comments, source=source))
                    else:
                        # Array simple, usar la clave determinada
                        lines.append(f'{key_name} = {elem.to_toml(comments=inline_comments, source=source)}')
                else:
                    # Si es valor simple, agregarlo con la clave determinada
                    lines.append(f'{key_name} = {elem.to_toml(comments=inline_comments, source=source)}')
                lines.append('')  # Línea vacía entre elementos
            result_lines.extend(lines)
        else:
            # Agregar comentarios iniciales
            if leading_comments:
                result_lines.extend(leading_comments)
            # Caso simple: value = ...
            result_lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
    else:
        # Agregar comentarios iniciales para tablas
        if leading_comments:
            result_lines.extend(leading_comments)
        result_lines.append(ast_node.to_toml(comments=inline_comments, source=source))
    
    # Agregar comentarios finales
    if trailing_comments:
        result_lines.append('')
        result_lines.extend(trailing_comments)
    
    return '\n'.join(result_lines).rstrip() + '\n' if result_lines else ''