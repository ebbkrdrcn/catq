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

    def Parse(self):
        has_lp = self.__ParseLeftParen()
        left = self.__ParseIdentifier()
        if self.__Peek().type == Token.Types.KEYWORD:
            expr = self.__ParseMethod(left)
            and_or_expr = self.__ParseAndOr(expr)
            if and_or_expr:
                expr = and_or_expr

            return expr
        else:
            expr = self.__ParseBinary(left)
            if expr:
                if not has_lp or self.__ParseRightParent():
                    and_or_expr = self.__ParseAndOr(expr)
                    if and_or_expr:
                        return and_or_expr

                    return expr

        self.__RaiseError(self.__Peek())

    def debug_string(self):
        r = self.Parse()
        return self.__ToJson(r)

    def __ParseLeftParen(self):
        return self.__ParseDelimiter("(")

    def __ParseRightParent(self):
        return self.__ParseDelimiter(")")

    def __ParseOperator(self):
        t = self.__Peek()
        if t.type == Token.Types.OPERATOR \
                and not re.match("^(and|or)$", self.__Peek().value):
            self.__Accept(Token.Types.OPERATOR)
            return True
        return False

    def __ParseAndOr(self, expr):
        has_lp = self.__ParseLeftParen()
        t = self.__Peek()
        if t.type == Token.Types.OPERATOR \
                and re.match("^(and|or)$", self.__Peek().value):
            self.__Accept(Token.Types.OPERATOR)
            expr = self.__ParseBinary(expr, op=t, right=self.Parse())
            if not has_lp or self.__ParseRightParent():
                return expr

        return None

    def __ParseBinary(self, left, op=None, right=None):
        if not op:
            op = self.__Peek()

        if not right:
            if self.__ParseOperator():
                right = self.__ParseLiteral()
            else:
                right = self.__ParseAndOr(left)

        if right:
            return Expression.New(Expression.BINARY, op.value, left, right)

        return None

    def __ParseIdentifier(self, depth=0):
        t = self.__Peek()
        if self.__Accept(Token.Types.IDENTIFIER):
            if not depth and self.__current_lp and\
                            self.__current_lp.value != t.value:
                self.__RaiseError(t)

            dt = self.__Peek()
            expr = None
            if dt.type == Token.Types.DELIMITER:
                if dt.value == "/":
                    self.__Accept(Token.Types.DELIMITER)
                    it = self.__Peek()
                    if it.type == Token.Types.IDENTIFIER:
                        expr = self.__ParseIdentifier(depth=depth + 1)
            return Expression.New(Expression.MEMBER, t.value, expr)
        return None

    def __ParseDelimiter(self, v):
        lp = self.__Peek()
        if lp.type == Token.Types.DELIMITER and lp.value == v:
            self.__Accept(Token.Types.DELIMITER)
            return True
        return False

    def __ParseLiteral(self):
        l = self.__Peek()
        if l.type == Token.Types.LITERAL:
            self.__Accept(Token.Types.LITERAL)
            return Expression.New(Expression.LITERAL, l.value)

        return None

    def __ParseMethod(self, member):
        k = self.__Peek()
        expr = None
        if k.type == Token.Types.KEYWORD:
            self.__Accept(Token.Types.KEYWORD)
            if self.__ParseLeftParen():
                if k.value == "any":
                    expr = Expression.New(Expression.METHOD_CALL, "any", member, expr=self.__ParseLambda())
                else:
                    expr = Expression.New(Expression.METHOD_CALL, k.value, member, args=self.__ParseMethodArgs())

                if self.__ParseRightParent():
                    return expr

        return None

    def __ParseLambda(self):
        it = self.__Peek()
        if self.__Accept(Token.Types.IDENTIFIER):
            if self.__ParseDelimiter(":"):
                self.__current_lp = it
                pe = Expression.New(Expression.PARAMETER, it.value)
                be = self.Parse()
                self.__current_lp = None
                return Expression.New(Expression.LAMBDA, pe, be)

        return None

    def __ParseMethodArgs(self, list=None):
        if not list:
            list = []

        expr = self.__ParseLiteral()
        if expr:
            list.append(expr)
            if self.__ParseDelimiter(","):
                return self.__ParseMethodArgs(list)

            return list

        self.__RaiseError(self.__Peek())

    def __Accept(self, type):
        if self.__Peek().type == type:
            if self.__tokenizer.HasNext():
                self.__current = self.__tokenizer.GetNextToken()
            return True
        return False

    def __Peek(self):
        if not self.__current:
            if self.__tokenizer.HasNext():
                self.__current = self.__tokenizer.GetNextToken()

        return self.__current

    def __RaiseError(self, *args):
        s = args[0].offset[0]
        e = args[len(args) - 1].offset[1]
        q = self.__query[0:e].split(' ')
        m = q.pop()
        if len(q) > 1:
            m = "%s %s" % (q.pop(), m)
            s = e - len(m)

        raise SyntaxError("Syntax error at position %s-%s on \"%s\"" % (s, e, m))

    def __ToJson(self, r):
        return r.ToJson()
