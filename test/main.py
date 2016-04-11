import re
from catq import Parser
from catq2mongo import CatQ2Mongo
from bson import ObjectId

if __name__ == "__main__":
    query = "Name/sub('movie') and Category/Id eq oid'507f1f77bcf86cd799439011'"
    parser = Parser(query)
    q = CatQ2Mongo().Visit(parser.Parse())
    e = {
        '$and': [
            {'Name': {'$regex': '/.*(movie).*/i'}},
            {'Category.Id': ObjectId('507f1f77bcf86cd799439011')}
        ]
    }

    assert q == e
    print q
