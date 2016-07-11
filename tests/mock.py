from pynYNAB.schema.budget import Budget, Account


class MockClient(object):
    def __init__(self):
        self.budget = Budget()
    def select_account_ui(self):
        return Account()
    def sync(self):
        pass