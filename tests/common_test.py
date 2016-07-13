import unittest

from sqlalchemy import create_engine

from pynYNAB.db import Base, Session


class commonTestCaseBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global transaction, connection, engine

        # Connect to the database and create the schema within a transaction
        engine = create_engine('sqlite:///:memory:')
        connection = engine.connect()
        transaction = connection.begin()
        Base.metadata.create_all(connection)

        Session.configure(bind=engine)

    @classmethod
    def tearDownClass(cl):
        # Roll back the top level transaction and disconnect from the database
        transaction.rollback()
        connection.close()
        engine.dispose()