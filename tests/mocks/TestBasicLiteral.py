testBooleanLiteralSourceTrue = {
    "ksonsource": """true""",
    "tomlexpected": """value = true"""
}

testBooleanLiteralSourceFalse = {
    "ksonsource": """false""",
    "tomlexpected": """value = false"""
}

testNullLiteralSource = {
    "ksonsource": """null""",
    "tomlexpected": """value = "null\""""
}

all_tests = [
    testBooleanLiteralSourceTrue,
    testBooleanLiteralSourceFalse,
    testNullLiteralSource
]