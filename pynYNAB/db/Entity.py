from sqlalchemy import Column
from sqlalchemy.orm import class_mapper
from sqlalchemy.types import Boolean,String
from sqlalchemy.ext.declarative import declared_attr

from pynYNAB import KeyGenerator

ignored_fields_for_hash = ['id', 'credit_amount', 'cash_amount']

class Entity(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(String(36),primary_key=True,default=KeyGenerator.generateuuid)
    is_tombstone = Column(Boolean())

    def getdict(self):
        result = {}
        for prop in class_mapper(self.__class__).iterate_properties:
            if isinstance(prop, Column):
                result[prop.key] = getattr(self, prop.key)
        return result

    def hash(self):
        t = tuple((k, v) for k, v in self.getdict().items() if k not in ignored_fields_for_hash)
        try:
            return hash(frozenset(t))
        except TypeError:
            pass