#!/usr/bin/python

import re

class Token:
    class Types:
        IDENTIFIER = "identifier"
        LITERAL = "literal"
        KEYWORD = "keyword"
        OPERATOR = "operator"
        DELIMITER = "delimiter"
        WHITESPACE = "whitespace"

    def __init__(self, value, type, offset):
        self.__value = value
        self.__type = type
        self.__offset = offset

    @property
    def value(self):
        return self.__value

    @property
    def type(self):
        return self.__type

    @property
    def offset(self):
        return self.__offset

    def __eq__(self, other):
        return self.type == other.type \
               and self.value == other.value;

    def __str__(self):
        return "%s, %s | %s | \"%s\"" % (self.__offset[0], self.__offset[1], self.type, self.__value)

class Tokenizer:
    KEYWORD_RE = re.compile("^(any|sub|startswith|endswith|in|nin)$")
    IDENTIFIER_RE = re.compile("^([_a-zA-Z][_a-zA-Z0-9]*)|\$$")
    OPERATOR_RE = re.compile("^(and|eq|(gte?)|(lte?)|ne|or)$")
    DELIMITER_RE = re.compile("[\(\)\/,\:]")
    WHITESPACE_RE = re.compile("^\s+$")
    LITERAL_RE = re.compile("^((\w+)?\'.*\')|(\d+)|(true|false)$")

    def __init__(self, query):
        if not query:
            raise ValueError("query")

        self.__query = query
        self.__pos = 0

    def get_next(self):
        s = ''
        instr = False
        esc = False
        x = None
        sp = self.__pos

        while self.__has_sym():
            x = self.__get_next_sym()
            if x == ' ':
                if not s:
                    s = x
                    break
                elif not instr:
                    self.__pos -= 1
                    break
            elif re.match(Tokenizer.DELIMITER_RE, x):
                if not instr:
                    if s:
                        self.__pos -= 1
                    else:
                        s = x

                    break
            elif x == '\'':
                if instr:
                    if not esc:
                        s += x
                        break
                else:
                    instr = True
            elif x == '\\':
                if not instr and not esc:
                    esc = True
                    s += x
                    continue
            if esc:
                esc = False

            s += x

        if s:
            t = self.__find_type(s)
            if t == Token.Types.WHITESPACE:
                return self.get_next()

            return Token(s, t, [sp, self.__pos])

        return None

    def has_next(self):
        return self.__has_sym()

    def __has_sym(self):
        return self.__pos < len(self.__query)

    def __get_next_sym(self):
        c = self.__query[self.__pos]
        self.__pos = self.__pos + 1
        return c

    def __find_type(self, value):
        if not value:
            raise ValueError("value")

        if self.__is_whitespace(value):
            return Token.Types.WHITESPACE
        elif self.__is_literal(value):
            return Token.Types.LITERAL
        elif self.__is_delimiter(value):
            return Token.Types.DELIMITER
        elif self.__is_keyword(value):
            return Token.Types.KEYWORD
        elif self.__is_operator(value):
            return Token.Types.OPERATOR
        elif self.__is_identifier(value):
            return Token.Types.IDENTIFIER

        return None

    def __is_whitespace(self, value):
        return re.match(Tokenizer.WHITESPACE_RE, value)

    def __is_delimiter(self, value):
        return re.match(Tokenizer.DELIMITER_RE, value)

    def __is_keyword(self, value):
        return re.match(Tokenizer.KEYWORD_RE, value)

    def __is_operator(self, value):
        return re.match(Tokenizer.OPERATOR_RE, value)

    def __is_identifier(self, value):
        return re.match(Tokenizer.IDENTIFIER_RE, value)

    def __is_literal(self, value):
        return re.match(Tokenizer.LITERAL_RE, value)