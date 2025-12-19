"""AST (Abstract Syntax Tree) para la conversión de KsonValue a TOML string."""

from kson import KsonValue, KsonValueType
from typing import Dict, List
import textwrap


class TomlNode:
    """Base class for all TOML AST nodes."""
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        raise NotImplementedError


class TomlString(TomlNode):
    """String representation in TOML."""
    
    def __init__(self, value: str, allow_multiline: bool = True):
        # Convert KSON whitespace escapes: $ + whitespace -> tab
        value = value.replace('$ ', '\t').replace('$\t', '\t')
        self.value = value
        self.allow_multiline = allow_multiline
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        has_real_newlines = '\n' in self.value
        has_real_tabs = '\t' in self.value
        
        # Use triple-quoted strings for multiline content
        if self.allow_multiline and (has_real_newlines or has_real_tabs) and len(self.value.strip()) > 0:
            return f'"""{self.value}"""'
        
        has_single_quote = "'" in self.value
        has_backslash = '\\' in self.value
        has_double_quote = '"' in self.value
        
        # Use single quotes when content has backslashes and double quotes but no single quotes
        if has_backslash and has_double_quote and not has_single_quote:
            escaped = self.value.replace('\\', '\\\\')
            return f"'{escaped}'"
        
        # Use double quotes by default, escaping in order: backslash, quotes, newlines
        escaped = self.value.replace('\\', '\\\\').replace('"', '\\"')
        if '\n' in escaped:
            escaped = escaped.replace('\n', '\\n')
        
        return f'"{escaped}"'


class TomlInteger(TomlNode):
    """Integer representation in TOML."""
    
    def __init__(self, value: int, literal: str = None):
        self.value = value
        self.literal = literal
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        return self.literal if self.literal else str(self.value)


class TomlFloat(TomlNode):
    """Float/decimal representation in TOML."""
    
    def __init__(self, value: float, literal: str = None):
        self.value = value
        self.literal = literal
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        return self.literal if self.literal else str(self.value)


class TomlBoolean(TomlNode):
    """Boolean representation in TOML."""
    
    def __init__(self, value: bool):
        self.value = value
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        return 'true' if self.value else 'false'


class TomlNull(TomlNode):
    """Null representation in TOML (converted to "null" string)."""
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        return '"null"'


class TomlArray(TomlNode):
    """Array representation in TOML."""
    
    def __init__(self, elements: List[TomlNode], start_line: int = None, end_line: int = None):
        self.elements = elements
        self.start_line = start_line
        self.end_line = end_line
    
    def check_heterogeneous(self) -> bool:
        """Check if array needs array-of-tables format (arrays-with-tables mixed with other types)."""
        if not self.elements:
            return False
        
        has_array_with_tables = False
        has_other_types = False
        
        for elem in self.elements:
            if isinstance(elem, TomlArray):
                if any(isinstance(e, TomlTable) for e in elem.elements):
                    has_array_with_tables = True
                else:
                    has_other_types = True
            else:
                has_other_types = True
        
        return has_array_with_tables and has_other_types
    
    def needs_array_of_tables_format(self) -> bool:
        """Check if array as root value needs array-of-tables format [[value]]."""
        if not self.elements:
            return False
        
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
        
        if has_array and (has_number or has_boolean or has_null or has_table):
            return True
        
        primitive_types_count = sum([has_string, has_number, has_boolean, has_null])
        return primitive_types_count >= 2
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        if comments is None:
            comments = {}
        
        if not self.elements:
            return '[]'
        
        has_tables = any(isinstance(elem, TomlTable) for elem in self.elements)
        has_arrays = any(isinstance(elem, TomlArray) for elem in self.elements)
        
        if has_tables:
            elements_str = ', '.join(
                elem.to_inline() if isinstance(elem, TomlTable) else elem.to_toml(indent_level, {}, source) 
                for elem in self.elements
            )
            return f'[{elements_str}]'
        
        if has_arrays or len(self.elements) > 3 or comments:
            return self._to_toml_multiline(indent_level, comments, source)
        
        elements_str = ', '.join(elem.to_toml(indent_level, {}, source) for elem in self.elements)
        return f'[{elements_str}]'
    
    def _to_toml_multiline(self, indent_level, comments, source):
        """Generate multiline array with comment handling."""
        indent = '    ' * indent_level
        next_indent = '    ' * (indent_level + 1)
        lines = ['[']
        
        if source and comments:
            sorted_comment_lines = sorted(comments.keys())
            compact_mode = len(sorted_comment_lines) == 1 and sorted_comment_lines[0] == -1
            elem_indent = indent if compact_mode else next_indent
            consumed_comment_lines = set()
            
            for i, elem in enumerate(self.elements):
                elem_comments = {}
                if isinstance(elem, TomlArray) and elem.start_line is not None and elem.end_line is not None:
                    for comment_line, comment_list in comments.items():
                        if comment_line >= 0 and elem.start_line <= comment_line <= elem.end_line:
                            elem_comments[comment_line] = comment_list
                            consumed_comment_lines.add(comment_line)
                
                if i < len(sorted_comment_lines):
                    line_num = sorted_comment_lines[i]
                    if line_num not in consumed_comment_lines:
                        comment_indent = indent if (line_num == -1 and compact_mode) else next_indent
                        for comment in comments[line_num]:
                            lines.append(f'{comment_indent}{comment}')
                
                elem_str = elem.to_toml(indent_level + 1 if not compact_mode else indent_level, elem_comments, source)
                if i < len(self.elements) - 1:
                    lines.append(f'{elem_indent}{elem_str},')
                else:
                    lines.append(f'{elem_indent}{elem_str}')
            
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


class TomlTable(TomlNode):
    """Table/object representation in TOML."""
    
    def __init__(self, properties: Dict[str, TomlNode]):
        self.properties = properties
    
    def to_inline(self) -> str:
        """Convert table to inline format {key = value}."""
        items = []
        for key, value in self.properties.items():
            if ' ' in key or '-' in key or key in ['false', 'true', 'null']:
                key_str = f'"{key}"'
            else:
                key_str = key
            
            value_str = value.to_toml(0)
            items.append(f'{key_str} = {value_str}')
        
        return '{' + ', '.join(items) + '}'
    
    def to_toml(self, indent_level=0, table_path='', comments=None, source=None) -> str:
        if comments is None:
            comments = {}
        
        lines = []
        
        # Build property comments map
        property_comments = {k: [] for k in self.properties.keys()}
        
        if source and comments:
            source_lines = source.split('\n')
            key_line = {}
            
            for line_num, line in enumerate(source_lines):
                stripped = line.strip()
                if ':' in stripped and not stripped.startswith('#'):
                    key_part = stripped.split(':', 1)[0].strip()
                    if key_part.startswith('"') and key_part.endswith('"'):
                        key_part = key_part[1:-1]
                    if key_part in self.properties:
                        key_line[key_part] = line_num
            
            # Build a list of (key, key_line_num) sorted by line number
            # This allows us to find comments that are before a key
            sorted_keys = sorted(key_line.items(), key=lambda x: x[1])
            
            for line_num, comment_list in comments.items():
                # Find which key this comment belongs to
                # It belongs to the first key that appears on or after this line
                for k, k_line in sorted_keys:
                    if line_num <= k_line:
                        property_comments[k].extend(comment_list)
                        break
        
        # Categorize properties while preserving order
        items_with_types = []
        for key, value in self.properties.items():
            if isinstance(value, TomlTable):
                item_type = 'nested_table'
            elif isinstance(value, TomlArray) and any(isinstance(elem, TomlTable) for elem in value.elements):
                item_type = 'nested_array'
            else:
                item_type = 'simple'
            items_with_types.append((key, value, item_type))
        
        # Check if we have both simple and nested items
        has_simple = any(t == 'simple' for _, _, t in items_with_types)
        has_nested = any(t in ('nested_table', 'nested_array') for _, _, t in items_with_types)
        
        # Track if we've emitted the header for simple values
        simple_section_header_emitted = False
        # Track if we're in a context after array of tables (which will need section headers for embeds)
        after_nested_array = False
        
        # Process items in original order
        for idx, (key, value, item_type) in enumerate(items_with_types):
            # Track if we just added a comment
            has_comment_for_this_key = bool(property_comments[key])
            
            # Add blank line after array of tables before next item
            if idx > 0 and items_with_types[idx - 1][2] == 'nested_array' and lines and not property_comments[key]:
                lines.append('')
            
            # Add blank line before comment if there's content and this is a comment
            if property_comments[key] and lines:
                lines.append('')
            
            for comment_text in property_comments[key]:
                lines.append(comment_text)
            
            if item_type == 'simple':
                # Emit table header before first simple value if there are nested structures
                if not simple_section_header_emitted and table_path and not after_nested_array:
                    # Add blank line before header if there's content already
                    if lines and has_nested:
                        lines.append('')
                    lines.append(f'[{table_path}]')
                    simple_section_header_emitted = True
                
                if isinstance(value, TomlEmbed) and key != 'embedContent':
                    # Emit embed as a table (always, especially when it has a tag)
                    full_path = f'{table_path}.{key}' if table_path else key
                    # Don't add blank line if we just added a comment (comment already has spacing)
                    if lines and not has_comment_for_this_key:
                        lines.append('')
                    lines.append(f'[{full_path}]')
                    if value.tag:
                        lines.append(f'embedTag = "{value.tag}"')
                    lines.append(f'embedContent = {value.to_toml(indent_level, {}, source)}')
                else:
                    if key == 'embedContent' and isinstance(value, TomlString):
                        value.allow_multiline = False
                        value_str = value.to_toml(indent_level, {}, source)
                        value.allow_multiline = True
                    else:
                        value_str = value.to_toml(indent_level, {}, source)
                    
                    if ' ' in key or '-' in key or key in ['false', 'true', 'null']:
                        lines.append(f'"{key}" = {value_str}')
                    else:
                        lines.append(f'{key} = {value_str}')
            
            elif item_type == 'nested_table':
                # Nested table
                full_path = f'{table_path}.{key}' if table_path else key
                if table_path:
                    # If we have a parent table path, emit the header and content separately
                    if lines:
                        lines.append('')
                    lines.append(f'[{full_path}]')
                    nested_content = value._to_toml_content(0, full_path, {}, source)
                    if nested_content:
                        lines.append(nested_content)
                else:
                    # If no parent path (root level), let the nested table emit everything
                    nested_output = value.to_toml(0, full_path, comments=comments, source=source)
                    if lines:
                        lines.append('')
                    lines.append(nested_output)
            
            elif item_type == 'nested_array':
                # Array of tables
                for elem in value.elements:
                    if isinstance(elem, TomlTable):
                        full_path = f'{table_path}.{key}' if table_path else key
                        if lines:
                            lines.append('')
                        lines.append(f'[[{full_path}]]')
                        nested_content = elem._to_toml_content(0, full_path, comments, source)
                        if nested_content:
                            lines.append(nested_content)
                # After emitting array of tables, mark that we're in post-array context
                # and reset the header emission flag so subsequent simple values will re-emit [table_path]
                after_nested_array = True
                simple_section_header_emitted = False
        
        return '\n'.join(lines)
    
    def _to_toml_content(self, indent_level=0, table_path='', comments=None, source=None) -> str:
        """Emit table content without the header."""
        if comments is None:
            comments = {}
        
        lines = []
        
        # Build property comments map
        property_comments = {k: [] for k in self.properties.keys()}
        
        if source and comments:
            source_lines = source.split('\n')
            key_line = {}
            
            for line_num, line in enumerate(source_lines):
                stripped = line.strip()
                if ':' in stripped and not stripped.startswith('#'):
                    key_part = stripped.split(':', 1)[0].strip()
                    if key_part.startswith('"') and key_part.endswith('"'):
                        key_part = key_part[1:-1]
                    if key_part in self.properties:
                        key_line[key_part] = line_num
            
            # Build a list of (key, key_line_num) sorted by line number
            # This allows us to find comments that are before a key
            sorted_keys = sorted(key_line.items(), key=lambda x: x[1])
            
            for line_num, comment_list in comments.items():
                # Find which key this comment belongs to
                # It belongs to the first key that appears on or after this line
                for k, k_line in sorted_keys:
                    if line_num <= k_line:
                        property_comments[k].extend(comment_list)
                        break
        
        # Categorize properties while preserving order
        items_with_types = []
        for key, value in self.properties.items():
            if isinstance(value, TomlTable):
                item_type = 'nested_table'
            elif isinstance(value, TomlArray) and any(isinstance(elem, TomlTable) for elem in value.elements):
                item_type = 'nested_array'
            else:
                item_type = 'simple'
            items_with_types.append((key, value, item_type))
        
        # Track if we're in a context after array of tables
        after_nested_array = False
        
        # Process items in original order
        for idx, (key, value, item_type) in enumerate(items_with_types):
            # Add blank line after array of tables before next item
            if idx > 0 and items_with_types[idx - 1][2] == 'nested_array' and lines:
                lines.append('')
            
            # Add blank line before comment if there's content and this is a comment
            if property_comments[key] and lines:
                lines.append('')
            
            for comment_text in property_comments[key]:
                lines.append(comment_text)
            
            if item_type == 'simple':
                if isinstance(value, TomlEmbed) and key != 'embedContent':
                    full_path = f'{table_path}.{key}' if table_path else key
                    if lines:
                        lines.append('')
                    lines.append(f'[{full_path}]')
                    if value.tag:
                        lines.append(f'embedTag = "{value.tag}"')
                    lines.append(f'embedContent = {value.to_toml(indent_level, {}, source)}')
                else:
                    # For regular simple values, if we're after arrays, emit table header first
                    if after_nested_array and table_path:
                        if lines:
                            lines.append('')
                        lines.append(f'[{table_path}]')
                        after_nested_array = False
                    
                    if key == 'embedContent' and isinstance(value, TomlString):
                        value.allow_multiline = False
                        value_str = value.to_toml(indent_level, {}, source)
                        value.allow_multiline = True
                    else:
                        value_str = value.to_toml(indent_level, {}, source)
                    
                    if ' ' in key or '-' in key or key in ['false', 'true', 'null']:
                        lines.append(f'"{key}" = {value_str}')
                    else:
                        lines.append(f'{key} = {value_str}')
            
            elif item_type == 'nested_table':
                # Nested table
                full_path = f'{table_path}.{key}' if table_path else key
                if lines:
                    lines.append('')
                lines.append(f'[{full_path}]')
                nested_content = value._to_toml_content(0, full_path, {}, source)
                if nested_content:
                    lines.append(nested_content)
            
            elif item_type == 'nested_array':
                # Array of tables
                for elem in value.elements:
                    if isinstance(elem, TomlTable):
                        full_path = f'{table_path}.{key}' if table_path else key
                        if lines:
                            lines.append('')
                        lines.append(f'[[{full_path}]]')
                        nested_content = elem._to_toml_content(0, full_path, {}, source)
                        if nested_content:
                            lines.append(nested_content)
                # Mark that we're after array of tables
                after_nested_array = True
        
        return '\n'.join(lines)


class TomlEmbed(TomlNode):
    """Embedded code block representation in TOML."""
    
    def __init__(self, content: str, tag: str = None, metadata: str = None, has_escapes: bool = False):
        self.content = content
        self.tag = tag
        self.metadata = metadata
        self.has_escapes = has_escapes
    
    def to_toml(self, indent_level=0, comments=None, source=None) -> str:
        content = self.content
        
        if not self.has_escapes:
            content = textwrap.dedent(content)
        
        if not content.endswith('\n'):
            content = content + '\n'
        
        # Escape backslashes to prevent invalid escape sequences
        content = content.replace('\\', '\\\\')
        
        return f'"""\n{content}"""'



def extract_literal_text(kson_value, tokens, source):
    """Extract literal text from source to preserve number formatting."""
    if tokens is None or source is None:
        return None
    
    try:
        start_pos = kson_value.start()
        end_pos = kson_value.end()
        
        start_line = start_pos.line()
        start_col = start_pos.column()
        end_line = end_pos.line()
        end_col = end_pos.column()
        
        lines = source.split('\n')
        
        if start_line == end_line:
            return lines[start_line][start_col:end_col]
        
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
    """Extract embed content, converting escapes for simple content."""
    content = kson_value.content()
    has_escapes = '%\\%' in content or '$\\$' in content or '\\' in content
    
    if '%\\%' in content or '$\\$' in content:
        has_kson_structure = (
            ':\n' in content or ':\r' in content or ': ' in content or
            '\n$' in content or '\n%' in content
        )
        
        if not has_kson_structure:
            content = content.replace('%\\%', '%%').replace('$\\$', '$$')
            has_escapes = False
    
    return content, has_escapes


def extract_comments_with_mapping(kson_string, tokens):
    """Extract and map comments from source code."""
    lines = kson_string.split('\n')
    
    token_lines = []
    for token in tokens:
        if token.text() and token.text().strip():
            token_lines.append(token.start().line())
    
    leading_comments = []
    inline_comments = {}
    trailing_comments = []
    
    pending_comments = []
    found_first_content = False
    
    for line_num, line in enumerate(lines):
        stripped = line.strip()
        
        if '#' in stripped and not stripped.startswith('#'):
            parts = stripped.split('#', 1)
            if len(parts) == 2:
                comment_text = parts[1]
                comment = ('# ' + comment_text[1:]) if comment_text.startswith(' ') else ('#' + comment_text)
                if not found_first_content:
                    leading_comments.append(comment)
                    found_first_content = True
                else:
                    if line_num + 1 not in inline_comments:
                        inline_comments[line_num + 1] = []
                    inline_comments[line_num + 1].append(comment)
        elif stripped.startswith('#'):
            pending_comments.append(stripped)
        elif stripped:
            if not found_first_content:
                if pending_comments:
                    leading_comments.extend(pending_comments)
                    pending_comments = []
                found_first_content = True
            else:
                if pending_comments:
                    inline_comments[line_num] = pending_comments.copy()
                    pending_comments = []
    
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
    """Convert KsonValue to TOML AST node."""
    value_type = kson_value.value_type()
    
    if value_type == KsonValueType.STRING:
        return TomlString(kson_value.value())
    elif value_type == KsonValueType.INTEGER:
        literal = extract_literal_text(kson_value, tokens, source)
        return TomlInteger(kson_value.value(), literal)
    elif value_type == KsonValueType.DECIMAL:
        literal = extract_literal_text(kson_value, tokens, source)
        return TomlFloat(kson_value.value(), literal)
    elif value_type == KsonValueType.BOOLEAN:
        return TomlBoolean(kson_value.value())
    elif value_type == KsonValueType.NULL:
        return TomlNull()
    elif value_type == KsonValueType.ARRAY:
        elements = [kson_value_to_ast(elem, tokens, source) for elem in kson_value.elements()]
        start_line = kson_value.start().line() if kson_value.start() else None
        end_line = kson_value.end().line() if kson_value.end() else None
        return TomlArray(elements, start_line=start_line, end_line=end_line)
    elif value_type == KsonValueType.OBJECT:
        properties = {}
        for key, value in kson_value.properties().items():
            properties[key] = kson_value_to_ast(value, tokens, source)
        return TomlTable(properties)
    elif value_type == KsonValueType.EMBED:
        content, has_escapes = extract_raw_embed_content(kson_value, tokens, source)
        return TomlEmbed(
            content=content,
            tag=kson_value.tag(),
            metadata=kson_value.metadata(),
            has_escapes=has_escapes
        )
    else:
        raise ValueError(f"Unsupported Kson value type: {value_type}")


def kson_to_toml_string(kson_value: KsonValue, comment_map: Dict = None, source: str = None, tokens: List = None) -> str:
    """Convert KsonValue to TOML string with preserved comments."""
    if comment_map is None:
        comment_map = {'leading': [], 'inline': {}, 'trailing': []}
    
    ast_node = kson_value_to_ast(kson_value, tokens, source)
    
    leading_comments = comment_map.get('leading', [])
    inline_comments = comment_map.get('inline', {})
    trailing_comments = comment_map.get('trailing', [])
    
    result_lines = []
    
    if not isinstance(ast_node, TomlTable):
        result_lines.extend(_handle_non_table_root(ast_node, leading_comments, inline_comments, source))
    else:
        if leading_comments:
            result_lines.extend(leading_comments)
        result_lines.append(ast_node.to_toml(comments=inline_comments, source=source))
    
    if trailing_comments:
        result_lines.append('')
        result_lines.extend(trailing_comments)
    
    return '\n'.join(result_lines).rstrip() + '\n' if result_lines else ''


def _handle_non_table_root(ast_node, leading_comments, inline_comments, source):
    """Handle root values that are not tables."""
    lines = []
    
    if isinstance(ast_node, TomlArray) and ast_node.needs_array_of_tables_format():
        if leading_comments:
            lines.extend(leading_comments)
        for elem in ast_node.elements:
            lines.append('[[value]]')
            lines.append(f'item = {elem.to_toml()}')
            lines.append('')
        if lines and lines[-1] == '':
            lines.pop()
    
    elif isinstance(ast_node, TomlArray) and not ast_node.check_heterogeneous():
        lines.extend(_handle_array_root(ast_node, leading_comments, inline_comments, source))
    
    elif isinstance(ast_node, TomlEmbed) and (ast_node.tag or ast_node.metadata):
        if leading_comments:
            lines.extend(leading_comments)
        tag_value = ast_node.tag if ast_node.tag else ast_node.metadata
        embed_table = TomlTable({'embedTag': TomlString(tag_value), 'embedContent': ast_node})
        lines.append('[embedBlock]')
        lines.append(embed_table.to_toml(comments=inline_comments, source=source))
    
    elif isinstance(ast_node, TomlEmbed):
        if leading_comments:
            lines.extend(leading_comments)
            lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
        else:
            lines.append(f'embedContent = {ast_node.to_toml(comments=inline_comments, source=source)}')
    
    elif isinstance(ast_node, TomlArray) and ast_node.check_heterogeneous():
        if leading_comments:
            lines.extend(leading_comments)
        lines.extend(_handle_heterogeneous_array(ast_node, inline_comments, source))
    
    else:
        if leading_comments:
            lines.extend(leading_comments)
        lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
    
    return lines


def _handle_array_root(ast_node, leading_comments, inline_comments, source):
    """Handle regular array as root value."""
    lines = []
    has_nested_arrays = any(isinstance(elem, TomlArray) for elem in ast_node.elements)
    inline_comment_count = len(inline_comments) if inline_comments else 0
    
    if leading_comments and has_nested_arrays and inline_comments and inline_comment_count >= 2:
        lines.extend(leading_comments)
        lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
    elif leading_comments and len(leading_comments) >= 2 and inline_comments:
        outer_leading = leading_comments[:-1]
        inner_leading = [leading_comments[-1]]
        lines.extend(outer_leading)
        combined_comments = {-1: inner_leading}
        combined_comments.update(inline_comments)
        lines.append(f'value = {ast_node.to_toml(comments=combined_comments, source=source)}')
    elif leading_comments:
        combined_comments = {-1: leading_comments}
        if inline_comments:
            combined_comments.update(inline_comments)
        lines.append(f'value = {ast_node.to_toml(comments=combined_comments, source=source)}')
    else:
        lines.append(f'value = {ast_node.to_toml(comments=inline_comments, source=source)}')
    
    return lines


def _handle_heterogeneous_array(ast_node, inline_comments, source):
    """Handle heterogeneous array (mixed types) as root value."""
    lines = []
    has_arrays = any(isinstance(elem, TomlArray) for elem in ast_node.elements)
    has_tables = any(isinstance(elem, TomlTable) for elem in ast_node.elements)
    key_name = 'list_item' if (has_arrays or has_tables) else 'item'
    
    for elem in ast_node.elements:
        lines.append('[[value]]')
        if isinstance(elem, TomlTable):
            lines.append(elem.to_toml(comments=inline_comments, source=source))
        elif isinstance(elem, TomlArray):
            has_inner_tables = any(isinstance(e, TomlTable) for e in elem.elements)
            if has_inner_tables:
                for table_elem in elem.elements:
                    if isinstance(table_elem, TomlTable):
                        lines.append(f'[[value.{key_name}]]')
                        lines.append(table_elem.to_toml(comments=inline_comments, source=source))
            else:
                lines.append(f'{key_name} = {elem.to_toml(comments=inline_comments, source=source)}')
        else:
            lines.append(f'{key_name} = {elem.to_toml(comments=inline_comments, source=source)}')
        lines.append('')
    
    return lines