from i2psam.utils import format_kw, format_token, parse_kw_tokens, tokenize_sam_line


def test_format_kw_bool_and_none():
    assert format_kw("SILENT", True) == "SILENT=true"
    assert format_kw("SILENT", False) == "SILENT=false"
    assert format_kw("OPTION", None) == ""


def test_format_token_quotes_and_escapes():
    assert format_token("plain") == "plain"
    assert format_token("two words") == '"two words"'
    assert format_token('a"b\\c') == '"a\\"b\\\\c"'


def test_parse_kw_tokens_and_bool_conversion():
    tokens = ["RESULT=OK", "SILENT=true", "SSL=0", "X=42", "NOSEP"]
    parsed = parse_kw_tokens(tokens)

    assert parsed["RESULT"] == "OK"
    assert parsed["SILENT"] is True
    assert parsed["SSL"] is False
    assert parsed["X"] == "42"
    assert "NOSEP" not in parsed


def test_tokenize_sam_line_handles_quoted_values():
    line = 'HELLO VERSION USER="john doe" PASSWORD="a\\"b"'
    assert tokenize_sam_line(line) == [
        "HELLO",
        "VERSION",
        "USER=john doe",
        'PASSWORD=a"b',
    ]
