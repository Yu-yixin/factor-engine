from __future__ import annotations

from factor_engine.errors import LexerError
from factor_engine.tokens import Token, TokenType


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.length = len(text)
        self.position = 0

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while self.position < self.length:
            current = self.text[self.position]

            if current.isspace():
                self.position += 1
                continue

            if current.isdigit() or current == ".":
                tokens.append(self._read_number())
                continue

            if current.isalpha() or current == "_":
                tokens.append(self._read_identifier_or_boolean())
                continue

            if current == "+":
                tokens.append(Token(TokenType.PLUS, current, self.position))
                self.position += 1
                continue

            if current == "-":
                tokens.append(Token(TokenType.MINUS, current, self.position))
                self.position += 1
                continue

            if current == "*":
                tokens.append(Token(TokenType.STAR, current, self.position))
                self.position += 1
                continue

            if current == "/":
                tokens.append(Token(TokenType.SLASH, current, self.position))
                self.position += 1
                continue

            if current == "(":
                tokens.append(Token(TokenType.LPAREN, current, self.position))
                self.position += 1
                continue

            if current == ")":
                tokens.append(Token(TokenType.RPAREN, current, self.position))
                self.position += 1
                continue

            if current == "[":
                tokens.append(Token(TokenType.LBRACKET, current, self.position))
                self.position += 1
                continue

            if current == "]":
                tokens.append(Token(TokenType.RBRACKET, current, self.position))
                self.position += 1
                continue

            if current == ",":
                tokens.append(Token(TokenType.COMMA, current, self.position))
                self.position += 1
                continue

            if current == ">":
                tokens.append(self._read_greater())
                continue

            if current == "<":
                tokens.append(self._read_less())
                continue

            if current == "=":
                tokens.append(self._read_equal())
                continue

            raise LexerError(
                f"Unexpected character '{current}' at position {self.position}"
            )

        tokens.append(Token(TokenType.EOF, "", self.position))
        return tokens

    def _read_number(self) -> Token:
        start = self.position
        dot_count = 0

        while self.position < self.length:
            current = self.text[self.position]
            if current == ".":
                dot_count += 1
                if dot_count > 1:
                    raise LexerError(f"Invalid number at position {start}")
                self.position += 1
                continue

            if current.isdigit():
                self.position += 1
                continue

            break

        value = self.text[start:self.position]

        if value == ".":
            raise LexerError(f"Invalid number at position {start}")

        return Token(TokenType.NUMBER, value, start)

    def _read_identifier_or_boolean(self) -> Token:
        start = self.position

        while self.position < self.length:
            current = self.text[self.position]
            if current.isalnum() or current == "_":
                self.position += 1
                continue
            break

        value = self.text[start:self.position]

        if value in {"true", "false"}:
            return Token(TokenType.BOOLEAN, value, start)
        if value == "and":
            return Token(TokenType.AND, value, start)
        if value == "or":
            return Token(TokenType.OR, value, start)
        if value == "not":
            return Token(TokenType.NOT, value, start)

        return Token(TokenType.IDENTIFIER, value, start)

    def _read_greater(self) -> Token:
        start = self.position
        self.position += 1

        if self.position < self.length and self.text[self.position] == "=":
            self.position += 1
            return Token(TokenType.GE, ">=", start)

        return Token(TokenType.GT, ">", start)

    def _read_less(self) -> Token:
        start = self.position
        self.position += 1

        if self.position < self.length and self.text[self.position] == "=":
            self.position += 1
            return Token(TokenType.LE, "<=", start)

        return Token(TokenType.LT, "<", start)

    def _read_equal(self) -> Token:
        start = self.position
        self.position += 1

        if self.position < self.length and self.text[self.position] == "=":
            self.position += 1
            return Token(TokenType.EQ, "==", start)

        return Token(TokenType.ASSIGN, "=", start)
