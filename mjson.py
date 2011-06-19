""" 
Drop in replacement for json module capable of handling object Ids.
"""

import json as _json
from txmongo._pymongo.objectid import ObjectId

class Json(object):
    """ ObjectId capable json replacement """
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return {"$oid": str(obj)}

    def object_hook(self, dct):
        if "$oid" in dct:
            return ObjectId(str(dct["$oid"]))
        return dct
    
    def dumps(self, obj):
        return _json.dumps(obj, default=self.default)
    
    def loads(self, data):
        return _json.loads(data, object_hook=self.object_hook)

json = Json()