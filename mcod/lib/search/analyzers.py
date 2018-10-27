from elasticsearch_dsl import analyzer, token_filter

__all__ = ('standard_analyzer', 'polish_analyzer')

polish_hunspell = token_filter(
    'pl',
    type="hunspell",
    locale="pl_PL",
    dedup=True
)

polish_stopwords = token_filter(
    'polish_stopwords',
    type="stop",
    ignore_case=True,
    stopwords_path='stopwords.txt'
)

standard_analyzer = analyzer(
    'standard_analyzer',
    tokenizer="standard",
    filter=["standard", polish_stopwords, "lowercase"],
    char_filter=["html_strip"]
)

polish_analyzer = analyzer(
    'polish_analyzer',
    tokenizer="standard",
    filter=["standard", polish_stopwords, "lowercase", polish_hunspell],
    char_filter=["html_strip"]
)
