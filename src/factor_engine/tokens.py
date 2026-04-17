from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TokenType(str, Enum):
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    BOOLEAN = "BOOLEAN"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"

    GT = "GT"
    LT = "LT"
    GE = "GE"
    LE = "LE"
    EQ = "EQ"
    ASSIGN = "ASSIGN"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"

    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    position: int
