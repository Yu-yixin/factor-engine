import pytest

from factor_engine.errors import LexerError
from factor_engine.lexer import Lexer
from factor_engine.tokens import TokenType


def test_tokenize_arithmetic_expression():
    tokens = Lexer("close / delay(close, 1) - 1").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.SLASH,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.COMMA,
        TokenType.NUMBER,
        TokenType.RPAREN,
        TokenType.MINUS,
        TokenType.NUMBER,
        TokenType.EOF,
    ]


def test_tokenize_boolean_keywords():
    tokens = Lexer("rank(close, ascending=false, pct=true)").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.COMMA,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.BOOLEAN,
        TokenType.COMMA,
        TokenType.IDENTIFIER,
        TokenType.ASSIGN,
        TokenType.BOOLEAN,
        TokenType.RPAREN,
        TokenType.EOF,
    ]


def test_tokenize_logical_keywords():
    tokens = Lexer("not is_null(close) and volume > 0 or false").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.NOT,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.AND,
        TokenType.IDENTIFIER,
        TokenType.GT,
        TokenType.NUMBER,
        TokenType.OR,
        TokenType.BOOLEAN,
        TokenType.EOF,
    ]


def test_tokenize_comparison_expression():
    tokens = Lexer("volume >= ts_mean(volume, 20)").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.GE,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.COMMA,
        TokenType.NUMBER,
        TokenType.RPAREN,
        TokenType.EOF,
    ]


def test_tokenize_list_literal():
    tokens = Lexer("seglen_mean(close, [3, 5, 2])").tokenize()

    assert [token.type for token in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.COMMA,
        TokenType.LBRACKET,
        TokenType.NUMBER,
        TokenType.COMMA,
        TokenType.NUMBER,
        TokenType.COMMA,
        TokenType.NUMBER,
        TokenType.RBRACKET,
        TokenType.RPAREN,
        TokenType.EOF,
    ]


def test_invalid_character_raises():
    with pytest.raises(LexerError, match="@"):
        Lexer("close @ open").tokenize()


def test_invalid_number_raises():
    with pytest.raises(LexerError):
        Lexer("1.2.3").tokenize()
