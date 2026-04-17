from __future__ import annotations

from factor_engine.ast_nodes import (
    BinaryOpNode,
    BooleanNode,
    CallNode,
    Expr,
    ListNode,
    NumberNode,
    UnaryOpNode,
    VariableNode,
)
from factor_engine.errors import ParserError
from factor_engine.tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    def parse(self) -> Expr:
        expr = self._parse_expression()

        if not self._check(TokenType.EOF):
            token = self._current()
            raise ParserError(
                f"Unexpected token '{token.value}' at position {token.position}"
            )

        return expr

    def _parse_expression(self) -> Expr:
        return self._parse_or()

    def _parse_or(self) -> Expr:
        expr = self._parse_and()

        while operator := self._match(TokenType.OR):
            right = self._parse_and()
            expr = BinaryOpNode(left=expr, operator=operator.value, right=right)

        return expr

    def _parse_and(self) -> Expr:
        expr = self._parse_not()

        while operator := self._match(TokenType.AND):
            right = self._parse_not()
            expr = BinaryOpNode(left=expr, operator=operator.value, right=right)

        return expr

    def _parse_not(self) -> Expr:
        if operator := self._match(TokenType.NOT):
            operand = self._parse_not()
            return UnaryOpNode(operator=operator.value, operand=operand)

        return self._parse_comparison()

    def _current(self) -> Token:
        return self.tokens[self.position]

    def _advance(self) -> Token:
        token = self.tokens[self.position]
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return token

    def _check(self, token_type: TokenType) -> bool:
        return self._current().type == token_type

    def _match(self, *token_types: TokenType) -> Token | None:
        current = self._current()
        if current.type in token_types:
            self._advance()
            return current
        return None

    def _expect(self, token_type: TokenType, message: str) -> Token:
        token = self._current()
        if token.type != token_type:
            raise ParserError(f"{message} at position {token.position}")
        self._advance()
        return token

    def _parse_comparison(self) -> Expr:
        expr = self._parse_term()

        while operator := self._match(
            TokenType.GT,
            TokenType.LT,
            TokenType.GE,
            TokenType.LE,
            TokenType.EQ,
        ):
            right = self._parse_term()
            expr = BinaryOpNode(left=expr, operator=operator.value, right=right)

        return expr

    def _parse_term(self) -> Expr:
        expr = self._parse_factor()

        while operator := self._match(TokenType.PLUS, TokenType.MINUS):
            right = self._parse_factor()
            expr = BinaryOpNode(left=expr, operator=operator.value, right=right)

        return expr

    def _parse_factor(self) -> Expr:
        expr = self._parse_unary()

        while operator := self._match(TokenType.STAR, TokenType.SLASH):
            right = self._parse_unary()
            expr = BinaryOpNode(left=expr, operator=operator.value, right=right)

        return expr

    def _parse_unary(self) -> Expr:
        if operator := self._match(TokenType.PLUS, TokenType.MINUS):
            operand = self._parse_unary()
            return UnaryOpNode(operator=operator.value, operand=operand)

        return self._parse_primary()

    def _parse_primary(self) -> Expr:
        if token := self._match(TokenType.NUMBER):
            return NumberNode(float(token.value))

        if token := self._match(TokenType.BOOLEAN):
            return BooleanNode(token.value == "true")

        if token := self._match(TokenType.IDENTIFIER):
            if self._check(TokenType.LPAREN):
                return self._parse_call(token.value)
            return VariableNode(token.value)

        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "Expected ')'")
            return expr

        if self._check(TokenType.LBRACKET):
            return self._parse_list_literal()

        token = self._current()
        raise ParserError(
            f"Unexpected token '{token.value}' at position {token.position}"
        )

    def _parse_call(self, name: str) -> Expr:
        self._expect(TokenType.LPAREN, "Expected '(' after function name")

        args: list[Expr] = []
        kwargs: dict[str, Expr] = {}

        if not self._check(TokenType.RPAREN):
            while True:
                if self._is_keyword_argument():
                    key_token = self._expect(
                        TokenType.IDENTIFIER,
                        "Expected keyword argument name",
                    )
                    self._expect(TokenType.ASSIGN, "Expected '=' in keyword argument")
                    value = self._parse_expression()
                    kwargs[key_token.value] = value
                else:
                    args.append(self._parse_expression())

                if not self._match(TokenType.COMMA):
                    break

        self._expect(TokenType.RPAREN, "Expected ')' after arguments")
        return CallNode(name=name, args=args, kwargs=kwargs)

    def _parse_list_literal(self) -> Expr:
        self._expect(TokenType.LBRACKET, "Expected '['")

        items: list[Expr] = []
        if not self._check(TokenType.RBRACKET):
            while True:
                items.append(self._parse_expression())
                if not self._match(TokenType.COMMA):
                    break

        self._expect(TokenType.RBRACKET, "Expected ']' after list literal")
        return ListNode(items=items)

    def _is_keyword_argument(self) -> bool:
        if self._current().type != TokenType.IDENTIFIER:
            return False

        next_position = self.position + 1
        if next_position >= len(self.tokens):
            return False

        return self.tokens[next_position].type == TokenType.ASSIGN
