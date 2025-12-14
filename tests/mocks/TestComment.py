testSourceWithComment = {
    "ksonsource": """
        # this is a comment
        string
    """,
    "tomlexpected": """
        # this is a comment
        value = "string"
    """
}

testSanityCheckCommentFreeCompiles = {
    "ksonsource": """
        key:
            value: 42
    """,
    "tomlexpected": """
        [key]
        value = 42
    """
}

testCommentPreservationOnDashLists = {
    "ksonsource": """
        # comment one
        - one
        # comment two
        - two
        # comment three.1
        # comment three.2
        - three
    """,
    "tomlexpected": """
        value = [
            # comment one
            "one",
            # comment two
            "two",
            # comment three.1
            # comment three.2
            "three"
        ]
    """
}

testMultipleCommentsOnNestedElements = {
    "ksonsource": """
        # first comment
        # second comment
        # third comment
        - one
        - two
    """,
    "tomlexpected": """
        value = [
        # first comment
        # second comment
        # third comment
        "one",
        "two"
        ]
    """
}

testCommentPreservationOnConstants = {
    "ksonsource": """
        # comment on a number
        4.5
    """,
    "tomlexpected": """
        # comment on a number
        value = 4.5
    """
}

testCommentPreservationOnConstants_2 = {
    "ksonsource": """
        # comment on a boolean
        false
    """,
    "tomlexpected": """
        # comment on a boolean
        value = false
    """
}

testCommentPreservationOnConstants_3 = {
    "ksonsource": """
        # comment on an identifier
        id
    """,
    "tomlexpected": """
        # comment on an identifier
        value = "id"
    """
}

testCommentPreservationOnConstants_4 = {
    "ksonsource": """
        # comment on a string
        'a string'
    """,
    "tomlexpected": """
        # comment on a string
        value = "a string"
    """
}

testTrailingCommentPreservationOnConstants = {
    "ksonsource": """
        # trailing comment
        4.5
    """,
    "tomlexpected": """
        # trailing comment
        value = 4.5
    """
}

testTrailingCommentPreservationOnConstants_2 = {
    "ksonsource": """
        # trailing comment
        false
    """,
    "tomlexpected": """
        # trailing comment
        value = false
    """
}

testTrailingCommentPreservationOnConstants_3 = {
    "ksonsource": """
        id # trailing comment
    """,
    "tomlexpected": """
        # trailing comment
        value = "id"
    """
}

testTrailingCommentPreservationOnConstants_4 = {
    "ksonsource": """
        # trailing comment
        'a string'
    """,
    "tomlexpected": """
        # trailing comment
        value = "a string"
    """
}

testCommentPreservationOnObjects = {
    "ksonsource": """
        # a comment
        # an odd but legal comment on this val
        key: val
        # another comment
        key2: val2
    """,
    "tomlexpected": """
        # a comment
        # an odd but legal comment on this val
        key = "val"
        # another comment
        key2 = "val2"
    """
}

testCommentsPreservationOnCommas = {
    "ksonsource": """
        # this comment should be preserved on this property
        key1: val1
        # as should this one
        key2: val2
    """,
    "tomlexpected": """
        # this comment should be preserved on this property
        key1 = "val1"
        # as should this one
        key2 = "val2"
    """
}

testCommentPreservationOnLists = {
    "ksonsource": """
        # comment on list
        # comment on first_element
        - first_element
        # comment on second_element
        - second_element
    """,
    "tomlexpected": """
        # comment on list
        value = [
            # comment on first_element
            "first_element",
            # comment on second_element
            "second_element"
        ]
    """
}

testCommentPreservationOnLists_2 = {
    "ksonsource": """
        # comment on first_element
        - first_element
        # comment on second_element
        - second_element
    """,
    "tomlexpected": """
        value = [
            # comment on first_element
            "first_element",
            # comment on second_element
            "second_element"
        ]
    """
}

testCommentPreservationOnLists_3 = {
    "ksonsource": """
        # a list of lists
        - 
        # trailing comment on constant element
        - 1.2
        # a nested list element
        - 2.2
        - 3.2
        =
        - 
        # a nested dash-delimited list
        - 
            - 10.2
            =
        # a further nested braced list
        # trailing comment on nested list
        - 
            - 4.2
            # a further nested braced list element
            - 5.2
            =
        - 
            - 9.2
            - 8.2
    """,
    "tomlexpected": """
    # a list of lists
    value = [
        [
            # trailing comment on constant element
            1.2,
            # a nested list element
            2.2,
            3.2
        ],
        [
            # a nested dash-delimited list
            [10.2],
            # a further nested braced list
            # trailing comment on nested list
            [
                # a further nested braced list element
                4.2,
                5.2
            ],
            [9.2, 8.2]
        ]
    ]
    """
}

testCommentPreservationOnEmbedBlocks = {
    "ksonsource": """
        # a comment on an embed block
        %
        embedded stuff
        %%
    """,
    "tomlexpected": '''
        # a comment on an embed block
        value = """
        embedded stuff
        """
    '''
}

testTrailingCommentOnLists = {
    "ksonsource": """
        # leading
        # trailing list brace
        # trailing "one"
        - one
        # trailing "two"
        - two
    """,
    "tomlexpected": """
        # leading
        # trailing list brace
        value = [
            # trailing "one"
            "one",
            # trailing "two"
            "two"
        ]
    """
}

testTrailingCommentsInObjects = {
    "ksonsource": """
        # leading
        # trailing
        keyword: value
    """,
    "tomlexpected": """
        # leading
        # trailing
        keyword = "value"
    """
}

testTrailingCommentsInObjects_2 = {
    "ksonsource": """
        # leading
        # trailing
        keyword: value
    """,
    "tomlexpected": """
        # leading
        # trailing
        keyword = "value"
    """
}

testDocumentEndComments = {
    "ksonsource": """
        null
        
        # these are some trailing
        # comments that would like 
        # to be preserved at the end
        # of the file
    """,
    "tomlexpected": """
        value = "null"
        
        # these are some trailing
        # comments that would like 
        # to be preserved at the end
        # of the file
    """
}

all_tests = [
    testSourceWithComment,
    testSanityCheckCommentFreeCompiles,
    testCommentPreservationOnDashLists,
    testMultipleCommentsOnNestedElements,
    testCommentPreservationOnConstants,
    testCommentPreservationOnConstants_2,
    testCommentPreservationOnConstants_3,
    testCommentPreservationOnConstants_4,
    testTrailingCommentPreservationOnConstants,
    testTrailingCommentPreservationOnConstants_2,
    testTrailingCommentPreservationOnConstants_3,
    testTrailingCommentPreservationOnConstants_4,
    testCommentPreservationOnObjects,
    testCommentsPreservationOnCommas,
    testCommentPreservationOnLists,
    testCommentPreservationOnLists_2,
    testCommentPreservationOnLists_3,
    testCommentPreservationOnEmbedBlocks,
    testTrailingCommentOnLists,
    testTrailingCommentsInObjects,
    testTrailingCommentsInObjects_2,
    testDocumentEndComments
]