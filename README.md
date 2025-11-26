# KSON2TOML

Librería oficial para la transformación de KSON a TOML.

## Descripción

`kson2toml` es una librería Python que permite convertir strings a formato [KSON](https://github.com/kson-org/kson) a formato [TOML](https://toml.io/) (Tom's Obvious, Minimal Language). Esta librería utiliza el parser oficial de KSON y genera TOML válido y legible.

## Instalación

```bash
pip install kson2toml
```

O clona este repositorio:

```bash
git clone https://github.com/Matoxx01/kson2toml.git
cd kson2toml
```

## Uso

### Uso Básico

```python
# Uso official
```

## Ejemplo de Conversión

### Entrada KSON:

```kson
person:
  name: 'Leonardo Bonacci'
  nickname: Fibonacci
  favorite_books:
    - title: Elements
      author: Euclid
    - title: Metaphysics
      author: Aristotle
  favorite_numbers:
    - - 0
      - 1
      - 1
      - 2
```

### Salida TOML:

```toml
name = "Leonardo Bonacci"
nickname = "Fibonacci"
favorite_books = [...]
favorite_numbers = [[0, 1, 1, 2]]
```

## API

### `kson2toml(kson_string: str) -> str`

Función principal que convierte un string KSON a TOML.

**Parámetros:**
- `kson_string` (str): String en formato KSON válido

**Retorna:**
- `str`: String en formato TOML

**Excepciones:**
- `ValueError`: Si el string KSON no es válido o contiene errores de sintaxis

## Estructura del Proyecto

```
kson2toml/
├── kson2toml/
│   ├── __init__.py         # Package initialization
│   ├── kson2toml.py        # Función principal de conversión
│   └── ast.py              # AST y clases para representar nodos TOML
├── tests/
│   ├── test.py             # Tests de validación
│   └── fibonacci_sequence.kson  # Archivo de ejemplo
├── app.py                  # Aplicación de ejemplo
├── Pipfile                 # Dependencias del proyecto
└── README.md               # Este archivo
```

## Clases AST

El módulo `ast.py` contiene las siguientes clases para representar el árbol de sintaxis abstracta:

- `TomlNode`: Clase base para todos los nodos
- `TomlString`: Representa strings
- `TomlInteger`: Representa enteros
- `TomlFloat`: Representa decimales
- `TomlBoolean`: Representa booleanos
- `TomlNull`: Representa valores nulos
- `TomlArray`: Representa arrays
- `TomlTable`: Representa tablas/objetos
- `TomlEmbed`: Representa bloques embebidos

## Desarrollo

### Ejecutar Tests

```bash
python tests/test.py
```

### Requisitos

- Python 3.13+
- `kson-lang`: Parser oficial de KSON
- `toml`: Parser y validador de TOML

## Licencia

Este proyecto es la librería oficial de conversión KSON a TOML.

## Contribuir

Las contribuciones son bienvenidas. Por favor, asegúrate de que el código pase todos los tests antes de enviar un pull request.
