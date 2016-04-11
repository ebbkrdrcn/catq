import re
from catq import Expression, ExpressionVisitor
from bson import ObjectId
from dateutil import parser

class CatQ2Mongo(ExpressionVisitor):
    def __init__(self):
        super(CatQ2Mongo, self).__init__()
        self.__param_expr = None
        self.__literal_encoders = {
            "datetime": lambda x: parser.parse(x),
            "oid": lambda x: ObjectId(x)
        }

    def Visit(self, expr):
        return super(CatQ2Mongo, self).Visit(expr)

    def VisitBinary(self, expr):
        q = {}
        left = self.Visit(expr.left)
        right = self.Visit(expr.right)
        if expr.operator == "and" \
                or expr.operator == "or":
            k = "$%s" % expr.operator
            if not q.has_key(k):
                q[k] = []
            q[k].append(left)
            q[k].append(right)
        elif expr.operator == 'eq':
            q[left] = right
        else:
            q[left] = {}
            q[left]["$%s" % expr.operator] = right

        return q

    def VisitMember(self, expr):
        if self.__param_expr:
            if expr.name == self.__param_expr.parameter:
                expr = expr.expr

        if expr.expr:
            return "%s.%s" % (expr.name, self.Visit(expr.expr))
        else:
            return expr.name

    def VisitLiteral(self, expr):
        for x in [self.__VisitNumber, self.__VisitString, self.__VisitBoolean]:
            result = x(expr)
            if result:
                return result

    def VisitMethodCall(self, expr):
        if expr.name == 'in':
            return self.__VisitIn(expr)
        if expr.name == 'nin':
            return self.__VisitNin(expr)
        if expr.name == 'sub':
            return self.__VisitSub(expr)
        if expr.name == 'startswith':
            return self.__VisitStartsWith(expr)
        if expr.name == 'endswith':
            return self.__VisitEndsWith(expr)
        if expr.name == 'any':
            return self.__VisitAny(expr)

    def VisitLambda(self, expr):
        self.__param_expr = expr.parameter
        if expr.body.type == Expression.METHOD_CALL:
            r = self.VisitMethodCall(expr.body)
        else:
            r = self.VisitBinary(expr.body)
        self.__param_expr = None
        return r

    def __VisitString(self, expr):
        result = re.match("^(?P<prefix>\w+)?\'(?P<value>.+)\'$", expr.value)
        if result:
            prefix = result.group("prefix")
            value = result.group("value")
            if prefix:
                if self.__literal_encoders.has_key(prefix):
                    return self.__literal_encoders[prefix](value)

                raise Exception("Prefix '%s' does not support" % prefix)
            else:
                return value
        return None

    def __VisitNumber(self, expr):
        result = re.search('^(?P<value>(\d+)(.\d+)?)$', expr.value)
        if result:
            v = float(result.group("value"))
            if v % 1:
                return float(v)
            else:
                return int(v)

        return None

    def __VisitBoolean(self, expr):
        result = re.match('^(true|false)$', expr.value)
        if result:
            return bool(expr.value)

        return None

    def __VisitIn(self, expr):
        l = self.VisitMember(expr.member)
        r = [self.VisitLiteral(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$in"] = r
        return q

    def __VisitNin(self, expr):
        l = self.VisitMember(expr.member)
        r = [self.VisitLiteral(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$nin"] = r
        return q

    def __VisitSub(self, expr):
        l = self.VisitMember(expr.member)
        r = [self.VisitLiteral(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$regex"] = "/.*(%s).*/i" % re.escape(r[0])
        return q

    def __VisitStartsWith(self, expr):
        l = self.VisitMember(expr.member)
        r = [self.VisitLiteral(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$regex"] = "/^(%s)/i" % re.escape(r[0])
        return q

    def __VisitEndsWith(self, expr):
        l = self.VisitMember(expr.member)
        r = [self.VisitLiteral(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$regex"] = "/(%s)$/i" % re.escape(r[0])
        return q

    def __VisitAny(self, expr):
        l = self.VisitMember(expr.member)
        r = self.VisitLambda(expr.expr)
        q = {}
        q[l] = {}
        q[l]["$elemMatch"] = r
        return q