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

    def visit(self, expr):
        return super(CatQ2Mongo, self).visit(expr)

    def visit_binary(self, expr):
        q = {}
        left = self.visit(expr.left)
        right = self.visit(expr.right)
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

    def visit_member(self, expr):
        if self.__param_expr:
            if expr.name == self.__param_expr.parameter:
                expr = expr.expr

        if expr.expr:
            return "%s.%s" % (expr.name, self.visit(expr.expr))
        else:
            return expr.name

    def visit_literal(self, expr):
        for x in [self.__visit_number, self.__visit_string, self.__visit_boolean]:
            result = x(expr)
            if result:
                return result

    def visit_method_call(self, expr):
        if expr.name == 'in':
            return self.__visit_in(expr)
        if expr.name == 'nin':
            return self.__visit_nin(expr)
        if expr.name == 'sub':
            return self.__visit_sub(expr)

        if expr.name == 'startswith':
            return self.__visit_startswith(expr)
        if expr.name == 'endswith':
            return self.__visit_endswith(expr)
        if expr.name == 'any':
            return self.__visit_any(expr)

    def visit_lambda(self, expr):
        self.__param_expr = expr.parameter
        if expr.body.type == Expression.METHOD_CALL:
            r = self.visit_method_call(expr.body)
        else:
            r = self.visit_binary(expr.body)
        self.__param_expr = None
        return r

    def __visit_string(self, expr):
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

    def __visit_number(self, expr):
        result = re.search('^(?P<value>(\d+)(.\d+)?)$', expr.value)
        if result:
            v = float(result.group("value"))
            if v % 1:
                return float(v)
            else:
                return int(v)

        return None

    def __visit_boolean(self, expr):
        result = re.match('^(true|false)$', expr.value)
        if result:
            return bool(expr.value)

        return None

    def __visit_in(self, expr):
        l = self.visit_member(expr.member)
        r = [self.visit_literal(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$in"] = r
        return q

    def __visit_nin(self, expr):
        l = self.visit_member(expr.member)
        r = [self.visit_literal(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$nin"] = r
        return q

    def __visit_sub(self, expr):
        l = self.visit_member(expr.member)
        r = [self.visit_literal(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$regex"] = "/.*(%s).*/i" % re.escape(r[0])
        return q

    def __visit_startswith(self, expr):
        l = self.visit_member(expr.member)
        r = [self.visit_literal(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$regex"] = "/^(%s)/i" % re.escape(r[0])
        return q

    def __visit_endswith(self, expr):
        l = self.visit_member(expr.member)
        r = [self.visit_literal(x) for x in expr.args]
        q = {}
        q[l] = {}
        q[l]["$regex"] = "/(%s)$/i" % re.escape(r[0])
        return q

    def __visit_any(self, expr):
        l = self.visit_member(expr.member)
        r = self.visit_lambda(expr.expr)
        q = {}
        q[l] = {}
        q[l]["$elemMatch"] = r
        return q