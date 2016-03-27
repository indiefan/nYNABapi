from pynYNAB.schema.budget import Budget


class MockClient(object):
    def __init__(self):
        self.budget = Budget()