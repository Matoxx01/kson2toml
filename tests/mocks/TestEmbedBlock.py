testEmbedBlockSource = {
    "ksonsource": """
        %
            this is a raw embed
        %%
    """,
    "tomlexpected": '''
        embedContent = """
        this is a raw embed
        """
    '''
}

testEmbedBlockSource_2 = {
    "ksonsource": """
        %sql
            select * from something
        %%
    """,
    "tomlexpected": '''
        [embedBlock]
        embedTag = "sql"
        embedContent = """
        select * from something
        """
    '''
}

testEmbedBlockSource_3 = {
    "ksonsource": """
        %sql: database
            select * from something
        %%
    """,
    "tomlexpected": '''
        [embedBlock]
        embedTag = "sql"
        embedContent = """
        select * from something
        """
    '''
}

testEmbedBlockSource_4 = {
    "ksonsource": """
        %sql: ::::::::::::database::::::
            select * from something
        %%
    """,
    "tomlexpected": '''
        [embedBlock]
        embedTag = "sql"
        embedContent = """
        select * from something
        """
    '''
}

testEmbedBlockWithAlternativeDelimiters = {
    "ksonsource": """
        %
            this is a raw embed with alternative delimiter
        %%
    """,
    "tomlexpected": '''
        embedContent = """
        this is a raw embed with alternative delimiter
        """
    '''
}

testEmbedBlockWithAlternativeDelimiters_2 = {
    "ksonsource": """
        %sql
            select * from something
        %%
    """,
    "tomlexpected": '''
        [embedBlock]
        embedTag = "sql"
        embedContent = """
        select * from something
        """
    '''
}

testEmbedBlockWithEscapes = {
    "ksonsource": """
    %
    this is an escaped delim %\%
    whereas in this case, this is not $\$
    %%
    """,
    "tomlexpected": '''
    embedContent = """
    %
    this is an escaped delim %%
    whereas in this case, this is not $$
    %%
    """
    '''
}

testEmbedBlockWithEscapes_2 = {
    "ksonsource": """
    $
    more %% %% %% than $\$ should yield a $\$-delimited block
    $$
    """,
    "tomlexpected": '''
    embedContent = """
    %
    more %% %% %% than $$ should yield a $$-delimited block
    %%
    """
    '''
}

testEmbedBlockWithAlternativeDelimiterAndEscapes = {
    "ksonsource": """
    $
    these double $\$ dollars are %%%% embedded but escaped
    $$
    """,
    "tomlexpected": '''
    embedContent = """
    these double $$ dollars are %%%% embedded but escaped
    """
    '''
}

testEmbedBlockEndingInSlash = {
    "ksonsource": """
        %
        %\%%
    """,
    "tomlexpected": '''
        embedContent = """
        %\
        """
    '''
}

testEmbedBlockTagsRetainment = {
    "ksonsource": """
        %
        content%%
    """,
    "tomlexpected": '''
        embedContent = """
        content
        """
    '''
}

testEmbedBlockTagsRetainment_2 = {
    "ksonsource": """
        %sql
        content%%
    """,
    "tomlexpected": '''
        [embedBlock]
        embedTag = "sql"
        embedContent = """
        content
        """
    '''
}

testEmbedBlockTagsRetainment_3 = {
    "ksonsource": """
        %: meta
        content%%
    """,
    "tomlexpected": '''
        [embedBlock]
        embedTag = "meta"
        embedContent = """
        content
        """
    '''
}

testEmbedBlockFromObject = {
    "ksonsource": """
        embedBlock: %
            content
            %%
    """,
    "tomlexpected": '''
        [embedBlock]
        embedContent = """
        content
        """
    '''
}

testEmbedBlockFromObject_2 = {
    "ksonsource": """
        embedBlock:
            embedContent: 'content\n'
            unrelatedKey: 'is not an embed block'
    """,
    "tomlexpected": r"""
        [embedBlock]
        embedContent = "content\n"
        unrelatedKey = "is not an embed block"
    """
}

testEmbedBlockFromObjectWithoutStrings = {
    "ksonsource": """
        embedBlock:
            embedContent:
            not: content
            .
            unrelatedKey: 'is not an embed block'
    """,
    "tomlexpected": """
        [embedBlock]
        "unrelatedKey" = "is not an embed block"
        
        [embedBlock.embedContent]
        not = "content"
    """
}

testEmbeddedEmbedBlockFromObject = {
    "ksonsource": """
        embedBlock: $
            embeddedEmbed: %
            EMBED CONTENT
            %%
            $$
    """,
    "tomlexpected": '''
        [embedBlock]
        embedContent = """
        embeddedEmbed: %
        EMBED CONTENT
        %%
        """
    '''
}

testEmbeddedEmbedBlockFromObject_2 = {
    "ksonsource": """
        embedBlock: %
            embeddedEmbed: $
            EMBED WITH %\\% CONTENT
            $$
            %%
    """,
    "tomlexpected": r'''
        [embedBlock]
        embedContent = """
        embeddedEmbed: $
        EMBED WITH %\\% CONTENT
        $$
        """
    '''
}

all_tests = [
    testEmbedBlockSource,
    testEmbedBlockSource_2,
    testEmbedBlockSource_3,
    testEmbedBlockSource_4,
    testEmbedBlockWithAlternativeDelimiters,
    testEmbedBlockWithAlternativeDelimiters_2,
    testEmbedBlockWithEscapes,
    testEmbedBlockWithEscapes_2,
    testEmbedBlockWithAlternativeDelimiterAndEscapes,
    testEmbedBlockEndingInSlash,
    testEmbedBlockTagsRetainment,
    testEmbedBlockTagsRetainment_2,
    testEmbedBlockTagsRetainment_3,
    testEmbedBlockFromObject,
    testEmbedBlockFromObject_2,
    testEmbedBlockFromObjectWithoutStrings,
    testEmbeddedEmbedBlockFromObject,
    testEmbeddedEmbedBlockFromObject_2
]