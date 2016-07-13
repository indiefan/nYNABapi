from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()


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


from contextlib import contextmanager

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker, mapper,scoped_session

from pynYNAB.schema.budget import *
from pynYNAB.schema.catalog import *

session_factory = sessionmaker(expire_on_commit=False)
Session=scoped_session(session_factory)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        pass
        #session.close()

@event.listens_for(mapper, 'init')
def auto_add(target, args, kwargs):
    session=Session()
    session.add(target)
    try:
        session.commit()
    except:
        session.rollback()
