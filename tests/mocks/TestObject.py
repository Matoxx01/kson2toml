testEmptyObjectSource = {
    "ksonsource": "{}",
    "tomlexpected": ""
}

testObjectSource = {
    "ksonsource": """
        key: val
        'string key': 66.3
        hello: "y'all"
    """,
    "tomlexpected": """
        key = "val"
        "string key" = 66.3
        hello = "y'all"
    """
}

testObjectCommaPrecedence = {
    "ksonsource": """
        - ObjA1: 1
        - ObjA2:
            - nested1: v
            - nested2: v
            - nested3: v
            =
        - ObjA3: 3
        - 'A string'
        - ObjB4: 4
    """,
    "tomlexpected": """
    value = [
        {ObjA1 = 1},
        {ObjA2 = [
            {nested1 = "v"},
            {nested2 = "v"},
            {nested3 = "v"}
        ]},
        {ObjA3 = 3},
        "A string",
        {ObjB4 = 4}
    ]
    """
}

testObjectSourceMixedWithStringContainingRawNewlines = {
    "ksonsource": """
        first: value
        second: 'this is a string with a
        raw newline in it and at its end
        '
    """,
    "tomlexpected": '''
        first = "value"
        second = """this is a string with a
        raw newline in it and at its end
        """
    '''
}

testProhibitedKey = {
    "ksonsource": """
        'false': 'false'
        'true': 'true'
        'null': 'null'
    """,
    "tomlexpected": """
        "false" = "false"
        "true" = "true"
        "null" = "null"
    """
}

testObjectSourceWithImmediateTrailingComment = {
    "ksonsource": """
        #comment
        a: b
    """,
    "tomlexpected": """
        #comment
        a = "b"
    """
}

testObjectSourceOptionalCommas = {
    "ksonsource": """
        key: val
        'string key': 66.3
        hello: "y'all"
    """,
    "tomlexpected": """
        key = "val"
        "string key" = 66.3
        hello = "y'all"
    """
}

testNestedNonDelimitedObjects = {
    "ksonsource": """
        key:
            nested_key: 10
            another_nest_key: 3
            .
        unnested_key: 44
    """,
    "tomlexpected": """
        unnested_key = 44
        
        [key]
        nested_key = 10
        another_nest_key = 3
    """
}

all_tests = [
    testEmptyObjectSource,
    testObjectSource,
    testObjectCommaPrecedence,
    testObjectSourceMixedWithStringContainingRawNewlines,
    testProhibitedKey,
    testObjectSourceWithImmediateTrailingComment,
    testObjectSourceOptionalCommas,
    testNestedNonDelimitedObjects
]