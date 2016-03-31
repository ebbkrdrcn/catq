# CatQ
Simple Resource Query Language like OData

```python
pip install catq
```

```python
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
```



**Query Operators**

 ```
eq            equal
gt            greater than
gte           greater than or equal
lt            less than
lte           less than or equal.
ne            not equal
in            in
nin           not in
startswith    matches the first part of strings.
endswith      matches the last part of strings.
sub           matches any part of strings.
any           determines any element in a collection matches a certain condition.
and           logical and
or            logical or
```

**Examples**

```
category/name eq 'movies' and like_count gte 100

contents/id/in(10,22,34,36)

contents/id/nin(10,22,34,36)

contents/name/startswith('movie')

contents/name/endswith('at')

contents/title/sub('programming')

contents/tags/any(tag:tag/name eq 'python')

contents/categories/any(category:category/title/sub('program'))
```



