from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from pynYNAB.config import echo

BaseModel = declarative_base()

engine = create_engine('sqlite:///:memory:',echo=echo)


class Base(BaseModel):
    __abstract__ = True

    def __init__(self, **kwargs):
        self.initialized = False
        super(Base, self).__init__(**kwargs)
        for attr in self.__mapper__.column_attrs:
            if attr.key in kwargs:
                continue

            # TODO: Support more than one value in columns?
            assert len(attr.columns) == 1
            col = attr.columns[0]

            if col.default:
                if not callable(col.default.arg):
                    setattr(self, attr.key, col.default.arg)
                else:
                    setattr(self, attr.key, col.default.arg(self))
        self.initialized = True
