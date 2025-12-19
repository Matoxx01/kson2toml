# KSON2TOML

Librería para la transformación de KSON a TOML.

## Descripción

`kson2toml` es una librería Python que permite convertir strings a formato [KSON](https://kson.org/) a formato [TOML](https://toml.io/) (Tom's Obvious, Minimal Language). Esta librería utiliza el parser oficial de KSON y genera TOML válido y legible.

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

### Aplicación Gráfica

Instala el paquete:

```bash
pip install kson2toml
```

Luego ejecuta:

```bash
kson2toml
```

### Uso en Código

```python
from kson2toml import kson2toml

resultado = kson2toml(string_kson)
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

## Contribuir

Las contribuciones son bienvenidas. Por favor, asegúrate de que el código pase todos los tests antes de enviar un pull request.