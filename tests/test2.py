import unittest

from pynYNAB.schema.budget import Account


class Tests(unittest.TestCase):
    def test_in(self):
        obj = Account()
        obj2 = Account()

        l = [obj]

        self.assertNotIn(obj2, l)
