from collections.abc import Iterable
from typing import Any
import shlex


_BOOL_TO_SAM = {True: "true", False: "false"}
_SAM_TO_BOOL = {"true": True, "false": False, "1": True, "0": False}


def _needs_quotes(value: str) -> bool:
    return any(ch.isspace() for ch in value) or '"' in value or "\\" in value


def _escape_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def format_token(token: str) -> str:
    if _needs_quotes(token):
        return f'"{_escape_value(token)}"'
    return token


def format_kw(key: str, value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        s = _BOOL_TO_SAM[value]
    else:
        s = str(value)

    s = format_token(s)
    return f"{key}={s}"


def parse_kw_tokens(tokens: Iterable[str]) -> dict[str, str]:
    out = {}
    for tok in tokens:
        if "=" not in tok:
            continue
        k, v = tok.split("=", 1)
        if v in _SAM_TO_BOOL:
            v = _SAM_TO_BOOL[v]
        out[k] = v
    return out


def tokenize_sam_line(line: str) -> list[str]:
    lexer = shlex.shlex(line, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)
