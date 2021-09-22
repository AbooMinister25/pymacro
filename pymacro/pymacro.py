import inspect
import typing
from io import BytesIO
import tokenize
from enum import Enum
from collections import namedtuple
import functools
import textwrap


class TokenKind(Enum):
    DEFINE = "DEFINE"
    IDENT = "IDENT"
    INTEGER = "INTEGER"


token = namedtuple("Token", ["kind", "text"])


class MacroLexer:
    def __init__(self, source: str):
        self.source = source
        self.iter_source = iter(source)
        self.pos = 0
        self.keywords = {"DEFINE": TokenKind.DEFINE}
        self.tokens = []

    def tokenize(self):
        while self.pos < len(self.source):
            char = self.advance()
            if char is None:
                break

            if char in (" ", "\r", "\t"):
                continue
            elif char.isnumeric():
                self.get_number(char)
            else:
                if char.isalpha() or char == "_":
                    self.get_identifier(char)

    def advance(self) -> typing.Optional[str]:
        try:
            self.pos += 1
            return next(self.iter_source)
        except StopIteration:
            return

    def add_token(self, kind: TokenKind, text: str):
        self.tokens.append(token(kind, text))

    def peek(self) -> typing.Optional[str]:
        if self.pos + 1 >= len(self.source):
            return
        else:
            return self.source[self.pos]

    def get_number(self, first_char: str):
        value = first_char

        if self.pos >= len(self.source):
            pass
        else:
            peeked_char = self.source[self.pos]

            while peeked_char is not None:
                if peeked_char.isnumeric():
                    next_val = self.advance()
                    value += next_val
                    peeked_char = self.peek()
                else:
                    break

        self.add_token(TokenKind.INTEGER, value)

    def get_identifier(self, first_char: str):
        value = first_char

        if self.pos >= len(self.source):
            pass
        else:
            peeked_char = self.source[self.pos]

            while peeked_char is not None:
                if peeked_char.isalnum() or peeked_char.isalnum() == "_":
                    next_val = self.advance()
                    value += next_val
                    peeked_char = self.peek()
                else:
                    break

        if self.keywords.get(value) is not None:
            kind = self.keywords[value]
            self.add_token(kind, value)
        else:
            self.add_token(TokenKind.IDENT, value)


class MacroParser:
    def __init__(self, tokens: list[token]):
        self.tokens = iter(tokens)

    def parse(self) -> str:
        tok = self.next()

        if tok is not None:
            if tok.kind == TokenKind.DEFINE:
                var_name = self.parse()
                var_value = self.parse()

                if var_name is not None and var_value is not None:
                    return f"{var_name} = {var_value}"
                else:
                    raise SyntaxError("Invalid number of values provided")
            elif tok.kind == TokenKind.IDENT:
                return tok.text
            elif tok.kind == TokenKind.INTEGER:
                return tok.text
            else:
                raise SyntaxError("Invalid Syntax")

    def next(self) -> typing.Optional[token]:
        try:
            return next(self.tokens)
        except StopIteration:
            return


def macro(func: typing.Callable):
    source_str = inspect.getsource(func)
    source_str = source_str.replace("@macro", "")
    source_str = source_str.replace(f"def {func.__name__}():", "")
    source_str = textwrap.dedent(source_str)

    tokens = tokenize.tokenize(BytesIO(source_str.encode("utf-8")).readline)
    for toktype, tokval, _, _, _ in tokens:
        if toktype == tokenize.COMMENT:
            lexer = MacroLexer(tokval.replace("#", ""))
            lexer.tokenize()

            parser = MacroParser(lexer.tokens)
            code = parser.parse()
            source_str = source_str.replace(tokval, code)

    @functools.wraps(func)
    def wrapper():
        exec(source_str)

    return wrapper
