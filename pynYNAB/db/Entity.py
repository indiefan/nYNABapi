from sqlalchemy import Column as OriginalColumn
from sqlalchemy.ext import hybrid
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import class_mapper
from sqlalchemy.types import Boolean, String, Date, Enum

from pynYNAB import KeyGenerator
from pynYNAB.db.Types import Amount, Converter, IgnorableString, IgnorableBoolean
from pynYNAB.schema import enums


class Column(OriginalColumn):
    pass


class EntityBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(String(36), primary_key=True, default=KeyGenerator.generateuuid)

    @classmethod
    def convert_in(cls, instance):
        # convert python values into stuff that the nYNAB API understands
        result = {}

        for v in class_mapper(cls).all_orm_descriptors:
            if v.extension_type is hybrid.HYBRID_PROPERTY:
                result[v.__name__] = v.fget(instance)

        for col in class_mapper(cls).columns:
            if isinstance(col, Column):
                colcls = col.type.__class__
                try:
                    val = getattr(instance, col.key)

                    if val is not None:
                        if colcls == Date:
                            val = Converter.date_in(val)
                        elif colcls == Amount:
                            val = Converter.amount_in(val)
                        elif colcls == Enum:
                            val = val.value
                    elif colcls == IgnorableString or colcls == IgnorableBoolean:
                        continue
                    result[col.key] = val
                except AttributeError:
                    pass

        return result

    @classmethod
    def convert_out(cls, d):
        # converts nYNAB API values (dict) into python values
        result = {}
        for col in class_mapper(cls).columns:
            if isinstance(col, Column):
                colcls = col.type.__class__
                val = d.get(col.key)
                if val is not None:
                    if colcls == Date:
                        val = Converter.date_out(val)
                    elif colcls == Amount:
                        val = Converter.amount_out(val)
                    elif colcls == Enum:
                        val = getattr(getattr(enums, col.type.name), val)
                result[col.key] = val
        return result

    def getdict(self):
        return self.__class__.convert_in(self)

    def __hash__(self):
        return hash(frozenset(self.getdict().items()))

    def __eq__(self, other):
        if isinstance(other, Entity):
            return other.getdict() == self.getdict()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Entity(EntityBase):
    is_tombstone = Column(Boolean(), default=False)
