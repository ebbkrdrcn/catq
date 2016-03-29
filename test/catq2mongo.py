import re
from catq import Expression, ExpressionVisitor
from bson import ObjectId
from dateutil import parser

class CatQ2Mongo(ExpressionVisitor):
    def __init__(self):
        super(CatQ2Mongo, self).__init__()
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
        if expr.operator == "and"\
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
            q[left]["$%s" % expr.operator]  = right

        return q

    def visit_member(self, expr):
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
        pass

    def visit_lambda(self, expr):
        pass


    def __visit_string(self, expr):
        result = re.search("^(?P<prefix>\w+)?\'(?P<value>.+)\'$", expr.value)
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