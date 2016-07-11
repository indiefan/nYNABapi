
from contextlib import contextmanager

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker, mapper,scoped_session

from pynYNAB.db import engine
from pynYNAB.schema.budget import *
from pynYNAB.schema.catalog import *


session_factory = sessionmaker(bind=engine, expire_on_commit=False)
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

Base.metadata.create_all(engine)

@event.listens_for(mapper, 'init')
def auto_add(target, args, kwargs):
    session=Session()
    session.add(target)
    try:
        session.commit()
    except:
        session.rollback()



