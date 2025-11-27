testNestedListAndObjectFormatting = {
    "ksonsource": """
    nested_obj:
        key: value
        .
    nested_list:
        - 1.1
        - 2.1
    """,
    "tomlexpected": """
    nested_list = [
        1.1,
        2.1
    ]
    
    [nested_obj]
    key = "value"
    """
}

testParsingMultiLevelMixedObjectsAndLists = {
    "ksonsource": """
    outer_key1:
        inner_key:
        - 1
        - 2
        - 3
        .
    outer_key2: value
    """,
    "tomlexpected": """
    outer_key2 = "value"
    
    [outer_key1]
    inner_key = [
        1,
        2,
        3
    ]
    """
}

testParsingMultiLevelMixedObjectsAndLists_2 = {
    "ksonsource": """
    - 
        - inner_key: x
        =
    - outer_list_elem
    """,
    "tomlexpected": """
    value = [
        [
        {inner_key = "x"}
        ],
        "outer_list_elem"
    ]
    """
}

all_tests = [
    testNestedListAndObjectFormatting,
    testParsingMultiLevelMixedObjectsAndLists,
    testParsingMultiLevelMixedObjectsAndLists_2,
]