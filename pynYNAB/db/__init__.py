from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

BaseModel = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

class Base(BaseModel):
    __abstract__ = True

    def __init__(self, **kwargs):
        for attr in self.__mapper__.column_attrs:
            if attr.key in kwargs:
                continue

            # TODO: Support more than one value in columns?
            assert len(attr.columns) == 1
            col = attr.columns[0]

            if col.default:
                if not callable(col.default.arg):
                    kwargs[attr.key] = col.default.arg
                else:
                    kwargs[attr.key] = col.default.arg(self)

        super(Base, self).__init__(**kwargs)