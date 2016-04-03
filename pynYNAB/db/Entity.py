from sqlalchemy import Column as OriginalColumn
from sqlalchemy.ext import hybrid
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.types import Boolean, String, Date, Enum
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import class_mapper, ColumnProperty

from pynYNAB import KeyGenerator
from pynYNAB.config import get_logger
from pynYNAB.db.Types import Amount, Converter, IgnorableString, IgnorableBoolean, Amounthybrid
from pynYNAB.schema import enums
import pprint


class Column(OriginalColumn):
    pass


class EntityBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(String(36), primary_key=True, default=KeyGenerator.generateuuid)

    def get_dict(self,convert=False):
        # convert python values into stuff that the nYNAB API understands
        result = {}
        cls = self.__class__

        for v in class_mapper(cls).all_orm_descriptors:
            if v.extension_type is hybrid.HYBRID_PROPERTY:
                val = v.fget(self)
                if convert:
                    if isinstance(v, Amounthybrid):
                        val = Converter.amount_in(val)
                result[v.__name__] = val

        for col in class_mapper(cls).columns:
            if isinstance(col, Column):
                colcls = col.type.__class__
                try:
                    val = getattr(self, col.key)
                    if convert:
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
    def from_dict(cls, dictionary):
        objdict = {}
        logger = get_logger()
        logger.debug('Filtering dict to create %s from dict %s' % (cls, dictionary))
        filtered = {k: v for k, v in dictionary.items() if k in cls.__mapper__.column_attrs}
        for key, value in filtered.items():
            try:
                field = class_mapper(cls).get_property(key)
            except InvalidRequestError:
                if key in cls.__mapper__.all_orm_descriptors:
                    logger.info('ignored a key in an incoming dictionary, most likely a calculated field')
                    pass
                else:
                    logger.error(
                        'Encountered unknown field %s in a dictionary to create an entity of type %s ' % (
                        key, cls))
                    logger.error(
                        'Most probably the YNAB API changed, please add that field to the entities schema')
                    raise ValueError()
            if isinstance(field, ColumnProperty):
                objdict[key] = value
        logger.debug('Creating a %s from dict %s' % (cls, objdict))
        return cls(**objdict)

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

    def __hash__(self):
        newd = ((k,v) for k,v in self.get_dict().items() if k != 'id')
        return frozenset(newd).__hash__()

    def __eq__(self, other):
        if isinstance(other, Entity):
            return hash(self) == hash(other)
        else:
            return False

    def __repr__(self):
        return pprint.pformat(self.get_dict())

    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self):
        return self.__class__.from_dict(self.get_dict())


class Entity(EntityBase):
    is_tombstone = Column(Boolean(), default=False)
