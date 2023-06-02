import json

class A:
    def __init__(self):
        self.a = 11
        self.b = 12

class AEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj ,A):
            return [obj.a, obj.b]
        return json.JSONEncoder.default(self, obj)
    
s=json.dumps(A(), cls=AEncoder)
print(s)

