testStringLiteralSource = {
    "ksonsource": """'This is a string'""",
    "tomlexpected": '''value = "This is a string"'''
}

testEmptyString = {
    "ksonsource": "''",
    "tomlexpected": '''value = ""'''
}

testStringWithRawWhitespace = {
    "ksonsource": """
    |'This is a string with raw, unescaped whitespace ${' '}|
    |${'\t'}tabbed-indented second line'
    """,
    "tomlexpected": """
    value = \"\"\"This is a string with raw, unescaped whitespace \t
\ttabbed-indented second line\"\"\"
    """
}

testStringEscapes = {
    "ksonsource": """
        'this\'ll need "escaping"'
    """,
    "tomlexpected": """
    value = \"this'll need \\\"escaping\\\"\"
    """
}

testBackslashEscaping = {
    "ksonsource": """
        'string with \\ and "'
    """,
    "tomlexpected": r'''
        value = 'string with \\ and "'
    '''
}

testBackslashEscaping_2 = {
    "ksonsource": """
        'string with \\"'
    """,
    "tomlexpected": """
        value = "string with \\\""
    """
}

testMultipleDelimiters = {
    "ksonsource": """
        'string \'with\' "quotes"'
    """,
    "tomlexpected": """
        value = "string 'with' \\\"quotes\\\""
    """
}

testEdgeCases = {
    "ksonsource": """
        '""'
    """,
    "tomlexpected": '''
        value = "\\"\\""
    '''
}

testEdgeCases_2 = {
    "ksonsource": """
        '\\"\\"'
    """,
    "tomlexpected": """
        value = "\\\"\\\""
    """
}

testBackslashSequences = {
    "ksonsource": """
        '\\n'
    """,
    "tomlexpected": """
        value = "\\n"
    """
}

testBackslashSequences_2 = {
    "ksonsource": """
        '\\'
    """,
    "tomlexpected": """
        value = "\\\\"
    """
}

testUnquotedNonAlphaNumericString = {
    "ksonsource": """
        水滴石穿
    """,
    "tomlexpected": """
        value = "水滴石穿"
    """
}

testReservedKeywordStringsAreQuoted = {
    "ksonsource": """
        Y
    """,
    "tomlexpected": """
        value = \"Y\"
    """
}

testReservedKeywordStringsAreQuoted_2 = {
    "ksonsource": """
        False
    """,
    "tomlexpected": """
        value = \"False\"
    """
}

testReservedKeywordStringsAreQuoted_3 = {
    "ksonsource": """
        Null
    """,
    "tomlexpected": """
        value = \"Null\"
    """
}

testReservedKeywordStringsAreQuoted_4 = {
    "ksonsource": """
        No
    """,
    "tomlexpected": """
        value = \"No\"
    """
}

all_tests = [
    testStringLiteralSource,
    testEmptyString,
    testStringWithRawWhitespace,
    testStringEscapes,
    testBackslashEscaping,
    testBackslashEscaping_2,
    testMultipleDelimiters,
    testEdgeCases,
    testEdgeCases_2,
    testBackslashSequences,
    testBackslashSequences_2,
    testUnquotedNonAlphaNumericString,
    testReservedKeywordStringsAreQuoted,
    testReservedKeywordStringsAreQuoted_2,
    testReservedKeywordStringsAreQuoted_3,
    testReservedKeywordStringsAreQuoted_4,
]