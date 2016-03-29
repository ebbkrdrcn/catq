import re
from catq import Parser
from catq2mongo import CatQ2Mongo
from bson import ObjectId

if __name__ == "__main__":
    query = "id eq oid'507f1f77bcf86cd799439011' and like_count gte 5"
    parser = Parser(query)
    q = CatQ2Mongo().visit(parser.parse())
    e = {
        '$and': [
            {'id': ObjectId('507f1f77bcf86cd799439011')},
            {'like_count': {'$gte': 5}}
        ]
    }

    assert q == e
    print q
