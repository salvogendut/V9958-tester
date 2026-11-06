"""Minimal KiCad S-expression reader/writer used by project generators."""

import json
import re


class A(str):
    pass


def parse(s):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', s))

    def read(token):
        if token == "(":
            result = []
            for token in tokens:
                if token == ")":
                    return result
                result.append(read(token))
            raise ValueError("Unterminated s-expression")
        return json.loads(token) if token.startswith('"') else A(token)

    return read(next(tokens))


def dump(value):
    if isinstance(value, list):
        return "(" + " ".join(dump(item) for item in value) + ")"
    return str(value) if isinstance(value, A) else json.dumps(value)


def nodes(value, key):
    return [item for item in value if isinstance(item, list) and item and item[0] == key]


def node(value, key):
    return next((item for item in value if isinstance(item, list) and item and item[0] == key), None)
