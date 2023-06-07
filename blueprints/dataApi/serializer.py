from sqlalchemy.inspection import inspect

class Serializer(object):
    @staticmethod
    def serialize(item):
        return {c: getattr(item, c) for c in inspect(item).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [Serializer.serialize(m) for m in l]