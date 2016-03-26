from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

from pynYNAB.db import engine
from pynYNAB.db.catalog import *

Session = sessionmaker(bind=engine, expire_on_commit=False)


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
        session.close()

Base.metadata.create_all(engine)
