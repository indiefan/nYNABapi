from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)


class Base(BaseModel):
    __abstract__ = True

    def __init__(self, **kwargs):
        self.initialized = False
        filteredkwargs = {k: v for k, v in kwargs.items() if k in self.__mapper__.column_attrs}
        super(Base, self).__init__(**filteredkwargs)
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
