testEmptyListSource = {
    "ksonsource": "<>",
    "tomlexpected": "value = []"
}

testSquareBracketListSource = {
    "ksonsource": """
        - 'a string'
    """,
    "tomlexpected": """
        value = [
            "a string"
        ]
    """
}

testSquareBracketListSource_2 = {
    "ksonsource": """
        - 42.4
        - 43.1
        - 44.7
    """,
    "tomlexpected": """
        value = [
            42.4,
            43.1,
            44.7
        ]
    """
}

testSquareBracketListSource_3 = {
    "ksonsource": """
        - true
        - false
        - null
    """,
    "tomlexpected": """
        [[value]]
        item = true
        
        [[value]]
        item = false
        
        [[value]]
        item = "null"
    """
}

testSquareBracketListSource_4 = {
    "ksonsource": """
        - true
        - false
        - 
            - 1.2
            - 3.4
            - 5.6
    """,
    "tomlexpected": """
        [[value]]
        item = true
        
        [[value]]
        item = false
        
        [[value]]
        item = [1.2, 3.4, 5.6]
    """
}

testDashListSource = {
    "ksonsource": """
        - 'a string'
    """,
    "tomlexpected": """
        value = [
            "a string"
        ]
    """
}

testDashListSource_2 = {
    "ksonsource": """
        - 42.4
        - 43.1
        - 44.7
    """,
    "tomlexpected": """
        value = [
            42.4,
            43.1,
            44.7
        ]
    """
}

testDelimitedDashList = {
    "ksonsource": "<>",
    "tomlexpected": "value = []"
}

testDelimitedDashList_2 = {
    "ksonsource": """
        - a
        - b
        - c
    """,
    "tomlexpected": """
        value = [
            "a",
            "b",
            "c"
        ]
    """
}

testDashListNestedWithCommaList = {
    "ksonsource": """
        - 
            - <>
    """,
    "tomlexpected": """
        value = [
            [
                []
            ]
        ]
    """
}

testDashListNestedWithObject = {
    "ksonsource": """
        - nestedDashList:
            - a
            - b
            - c
    """,
    "tomlexpected": """
        value = [
            {nestedDashList = [
                "a",
                "b",
                "c"
            ]}
        ]
    """
}

testDashListNestedWithDashList = {
    "ksonsource": """
        - 
            - a
            - b
            - 
            - a1
            - b1
            - c1
            =
        - c
    """,
    "tomlexpected": """
        value = [
            [
                "a",
                "b",
                "",
                "a1",
                "b1",
                "c1"
            ],
                "c"
        ]
    """
}

testCommaFreeList = {
    "ksonsource": """
        - null
        - true
        - 
            - sublist
            =
        - 
            - another
            - sublist
    """,
    "tomlexpected": """
        [[value]]
        item = "null"
        
        [[value]]
        item = true
        
        [[value]]
        item = ["sublist"]
        
        [[value]]
        item = ["another", "sublist"]
    """
}

testNestedNonDelimitedDashLists = {
    "ksonsource": """
        - 
            - 'sub-list elem 1'
            - 'sub-list elem 2'
            =
        - 'outer list elem 1'
    """,
    "tomlexpected": """
        [[value]]
        item = ["sub-list elem 1", "sub-list elem 2"]
        
        [[value]]
        item = "outer list elem 1"
    """
}

all_tests = [
    testEmptyListSource,
    testSquareBracketListSource,
    testSquareBracketListSource_2,
    testSquareBracketListSource_3,
    testSquareBracketListSource_4,
    testDashListSource,
    testDashListSource_2,
    testDelimitedDashList,
    testDelimitedDashList_2,
    testDashListNestedWithCommaList,
    testDashListNestedWithObject,
    testDashListNestedWithDashList,
    testCommaFreeList,
    testNestedNonDelimitedDashLists
]