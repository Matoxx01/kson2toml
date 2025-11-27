testNumberLiteralSource = {
    "ksonsource": "42",
    "tomlexpected": "value = 42"
}

testNumberLiteralSource_float = {
    "ksonsource": "42.1",
    "tomlexpected": "value = 42.1"
}

testNumberLiteralSource_2 = {
    "ksonsource": "42.1e0",
    "tomlexpected": "value = 42.1e0"
}

testNumberLiteralSource_3 = {
    "ksonsource": "4.21e1",
    "tomlexpected": "value = 4.21e1"
}

testNumberLiteralSource_4 = {
    "ksonsource": "421e-1",
    "tomlexpected": "value = 421e-1"
}

testNumberLiteralSource_5 = {
    "ksonsource": "4210e-2",
    "tomlexpected": "value = 4210e-2"
}

testNumberLiteralSource_6 = {
    "ksonsource": "0.421e2",
    "tomlexpected": "value = 0.421e2"
}

testNumberLiteralSource_7 = {
    "ksonsource": "0.421e+2",
    "tomlexpected": "value = 0.421e+2"
}

testNumberLiteralSource_8 = {
    "ksonsource": "42.1e0",
    "tomlexpected": "value = 42.1e0"
}

testNegativeNumberLiteralSource_float = {
    "ksonsource": "-42.1",
    "tomlexpected": "value = -42.1"
}

testNegativeNumberLiteralSource_2 = {
    "ksonsource": "-42.1e0",
    "tomlexpected": "value = -42.1e0"
}

testNegativeNumberLiteralSource_3 = {
    "ksonsource": "-4.21e1",
    "tomlexpected": "value = -4.21e1"
}

testNegativeNumberLiteralSource_4 = {
    "ksonsource": "-421e-1",
    "tomlexpected": "value = -421e-1"
}

testNegativeNumberLiteralSource_5 = {
    "ksonsource": "-4210e-2",
    "tomlexpected": "value = -4210e-2"
}

testNegativeNumberLiteralSource_6 = {
    "ksonsource": "-0.421e2",
    "tomlexpected": "value = -0.421e2"
}

testNegativeNumberLiteralSource_7 = {
    "ksonsource": "-0.421e+2",
    "tomlexpected": "value = -0.421e+2"
}

testNegativeNumberLiteralSource_8 = {
    "ksonsource": "-42.1e0",
    "tomlexpected": "value = -42.1e0"
}

all_tests = [
    testNumberLiteralSource,
    testNumberLiteralSource_float,
    testNumberLiteralSource_2,
    testNumberLiteralSource_3,
    testNumberLiteralSource_4,
    testNumberLiteralSource_5,
    testNumberLiteralSource_6,
    testNumberLiteralSource_7,
    testNumberLiteralSource_8,
    testNegativeNumberLiteralSource_float,
    testNegativeNumberLiteralSource_2,
    testNegativeNumberLiteralSource_3,
    testNegativeNumberLiteralSource_4,
    testNegativeNumberLiteralSource_5,
    testNegativeNumberLiteralSource_6,
    testNegativeNumberLiteralSource_7,
    testNegativeNumberLiteralSource_8
]