#!/usr/bin/python

import re
from expression import Expression
from tokenizer import Token, Tokenizer

class Parser:
    def __init__(self, query):
        self.__stack = []
        self.__query = query
        self.__tokenizer = Tokenizer(query)
        self.__current = None
        self.__current_lp = None

    def parse(self):
        has_lp = self.__parse_left_paren()
        left = self.__parse_identifier()
        if self.__peek().type == Token.Types.KEYWORD:
            expr = self.__parse_method(left)
            and_or_expr = self.__parse_and_or(expr)
            if and_or_expr:
                expr = and_or_expr

            return expr
        else:
            expr = self.__parse_binary(left)
            if expr:
                if not has_lp or self.__parse_right_paren():
                    and_or_expr = self.__parse_and_or(expr)
                    if and_or_expr:
                        return and_or_expr

                    return expr

        self.__error(self.__peek())

    def debug_string(self):
        r = self.parse()
        return self.__to_json(r)

    def __parse_left_paren(self):
        return self.__parse_delimiter("(")

    def __parse_right_paren(self):
        return self.__parse_delimiter(")")

    def __parse_operator(self):
        t = self.__peek()
        if t.type == Token.Types.OPERATOR \
                and not re.match("^(and|or)$", self.__peek().value):
            self.__accept(Token.Types.OPERATOR)
            return True
        return False

    def __parse_and_or(self, expr):
        has_lp = self.__parse_left_paren()
        t = self.__peek()
        if t.type == Token.Types.OPERATOR \
                and re.match("^(and|or)$", self.__peek().value):
            self.__accept(Token.Types.OPERATOR)
            expr = self.__parse_binary(expr, op=t, right=self.parse())
            if not has_lp or self.__parse_right_paren():
                return expr

        return None

    def __parse_binary(self, left, op=None, right=None):
        if not op:
            op = self.__peek()

        if not right:
            if self.__parse_operator():
                right = self.__parse_literal()
            else:
                right = self.__parse_and_or(left)

        if right:
            return Expression.New(Expression.BINARY, op.value, left, right)

        return None

    def __parse_identifier(self, depth=0):
        t = self.__peek()
        if self.__accept(Token.Types.IDENTIFIER):
            if not depth and self.__current_lp and\
                            self.__current_lp.value != t.value:
                self.__error(t)

            dt = self.__peek()
            expr = None
            if dt.type == Token.Types.DELIMITER:
                if dt.value == "/":
                    self.__accept(Token.Types.DELIMITER)
                    it = self.__peek()
                    if it.type == Token.Types.IDENTIFIER:
                        expr = self.__parse_identifier(depth=depth + 1)
            return Expression.New(Expression.MEMBER, t.value, expr)
        return None

    def __parse_delimiter(self, v):
        lp = self.__peek()
        if lp.type == Token.Types.DELIMITER and lp.value == v:
            self.__accept(Token.Types.DELIMITER)
            return True
        return False

    def __parse_literal(self):
        l = self.__peek()
        if l.type == Token.Types.LITERAL:
            self.__accept(Token.Types.LITERAL)
            return Expression.New(Expression.LITERAL, l.value)

        return None

    def __parse_method(self, member):
        k = self.__peek()
        expr = None
        if k.type == Token.Types.KEYWORD:
            self.__accept(Token.Types.KEYWORD)
            if self.__parse_left_paren():
                if k.value == "any":
                    expr = Expression.New(Expression.METHOD_CALL, "any", member, expr=self.__parse_lambda())
                else:
                    expr = Expression.New(Expression.METHOD_CALL, k.value, member, args=self.__parse_method_arguments())

                if self.__parse_right_paren():
                    return expr

        return None

    def __parse_lambda(self):
        it = self.__peek()
        if self.__accept(Token.Types.IDENTIFIER):
            if self.__parse_delimiter(":"):
                self.__current_lp = it
                pe = Expression.New(Expression.PARAMETER, it.value)
                be = self.parse()
                self.__current_lp = None
                return Expression.New(Expression.LAMBDA, pe, be)

        return None

    def __parse_method_arguments(self, list=None):
        if not list:
            list = []

        expr = self.__parse_literal()
        if expr:
            list.append(expr)
            if self.__parse_delimiter(","):
                return self.__parse_method_arguments(list)

            return list

        self.__error(self.__peek())

    def __accept(self, type):
        if self.__peek().type == type:
            if self.__tokenizer.has_next():
                self.__current = self.__tokenizer.get_next()
            return True
        return False

    def __peek(self):
        if not self.__current:
            if self.__tokenizer.has_next():
                self.__current = self.__tokenizer.get_next()

        return self.__current

    def __error(self, *args):
        s = args[0].offset[0]
        e = args[len(args) - 1].offset[1]
        q = self.__query[0:e].split(' ')
        m = q.pop()
        if len(q) > 1:
            m = "%s %s" % (q.pop(), m)
            s = e - len(m)

        raise SyntaxError("Syntax error at position %s-%s on \"%s\"" % (s, e, m))

    def __to_json(self, r):
        return r.to_json()
