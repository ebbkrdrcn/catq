#!/usr/bin/python

class Expression(object):
    BINARY = "binary"
    MEMBER = "member"
    PARAMETER = "parameter"
    LITERAL = "literal"
    METHOD_CALL = "method_call"
    LAMBDA = "lambda"

    def __init__(self, type):
        self._type = type

    @staticmethod
    def New(type, *args, **kwargs):
        if type == Expression.MEMBER:
            return MemberExpression(*args, **kwargs)

        if type == Expression.PARAMETER:
            return ParameterExpression(*args)

        if type == Expression.LITERAL:
            return LiteralExpression(*args)

        if type == Expression.BINARY:
            return BinaryExpression(*args)

        if type == Expression.METHOD_CALL:
            return MethodCallExpression(*args, **kwargs)

        if type == Expression.LAMBDA:
            return LambdaExpression(*args)

        raise ValueError("invalid expression!")

    @property
    def type(self):
        return self._type

class BinaryExpression(Expression):
    def __init__(self, operator, left, right):
        super(BinaryExpression, self) \
            .__init__(Expression.BINARY)

        self.__operator = operator
        self.__left = left
        self.__right = right

    @property
    def right(self):
        return self.__right

    @property
    def operator(self):
        return self.__operator

    @property
    def left(self):
        return self.__left

    def ToJson(self):
        return dict(
            type=self.type,
            operator=self.__operator,
            left=self.__left.ToJson(),
            right=self.__right.ToJson()
        )

class MemberExpression(Expression):
    def __init__(self, name, expr=None):
        if not name:
            raise AttributeError("name")

        self.__name = name
        self.__expr = expr

        super(MemberExpression, self) \
            .__init__(Expression.MEMBER)

    @property
    def name(self):
        return self.__name

    @property
    def expr(self):
        return self.__expr

    def ToJson(self):
        return dict(
            type=self.type,
            name=self.__name,
            expr=self.__expr.ToJson() if self.__expr else None
        )

class ParameterExpression(Expression):
    def __init__(self, name):
        if not name:
            raise AttributeError("name")

        self.__parameter = name
        super(ParameterExpression, self) \
            .__init__(Expression.PARAMETER)

    @property
    def parameter(self):
        return self.__parameter

    def ToJson(self):
        return dict(
            type=self.type,
            parameter=self.parameter
        )

class LiteralExpression(Expression):
    def __init__(self, value):
        self.__value = value
        super(LiteralExpression, self) \
            .__init__(Expression.LITERAL)

    @property
    def value(self):
        return self.__value

    def ToJson(self):
        return dict(
            type=self.type,
            value=self.__value
        )

class MethodCallExpression(Expression):
    def __init__(self, name, member, expr=None, args=None):
        self.__name = name
        self.__member = member
        self.__args = args
        self.__expr = expr

        super(MethodCallExpression, self) \
            .__init__(Expression.METHOD_CALL)

    @property
    def name(self):
        return self.__name

    @property
    def member(self):
        return self.__member

    @property
    def args(self):
        return self.__args

    @property
    def expr(self):
        return self.__expr

    def ToJson(self):
        args = []
        if self.__args:
            for x in self.__args:
                args.append(x.ToJson())

        return dict(
            type=self.type,
            name=self.__name,
            member=self.__member.ToJson(),
            expr=self.__expr.ToJson() if self.__expr else None,
            args=args
        )

class LambdaExpression(Expression):
    def __init__(self, parameter, body):
        if not parameter:
            raise AttributeError("parameter")

        self.__body = body
        self.__parameter = parameter

        super(LambdaExpression, self) \
            .__init__(Expression.LAMBDA)

    @property
    def parameter(self):
        return self.__parameter

    @property
    def body(self):
        return self.__body

    def ToJson(self):
        return dict(
            type=self.type,
            parameter=self.__parameter.ToJson(),
            body=self.__body.ToJson()
        )

class ExpressionVisitor(object):
    def Visit(self, expr):
        if expr.type == Expression.BINARY:
            return self.VisitBinary(expr)
        elif expr.type == Expression.MEMBER:
            return self.VisitMember(expr);
        elif expr.type == Expression.PARAMETER:
            return self.VisitParameter(expr);
        elif expr.type == Expression.LITERAL:
            return self.VisitLiteral(expr);
        elif expr.type == Expression.METHOD_CALL:
            return self.VisitMethodCall(expr);
        elif expr.type == Expression.LAMBDA:
            return self.VisitLambda(expr);

    def VisitBinary(self, expr):
        pass

    def VisitMember(self, expr):
        pass

    def VisitParameter(self, expr):
        pass

    def VisitLiteral(self, expr):
        pass

    def VisitMethodCall(self, expr):
        pass

    def VisitLambda(self, expr):
        pass