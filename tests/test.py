import json
import unittest
from datetime import datetime

from sqlalchemy import Date

from pynYNAB.connection import ComplexEncoder
from pynYNAB.db import Base
from pynYNAB.db.Entity import Column
from pynYNAB.db.Types import Amount
from pynYNAB.db.db import session_scope
from pynYNAB.schema.budget import Account, AccountCalculation, AccountMapping, MasterCategory, Transaction, SubCategory, \
    MonthlyAccountCalculation, MonthlyBudget, MonthlySubCategoryBudget, MonthlyBudgetCalculation, \
    MonthlySubCategoryBudgetCalculation, PayeeLocation, Payee, PayeeRenameCondition, ScheduledSubtransaction, \
    ScheduledTransaction, Setting, Subtransaction, Budget, BudgetEntity
from pynYNAB.schema.catalog import BudgetVersion, User, UserBudget, UserSetting

types = [
    Account,
    AccountCalculation,
    AccountMapping,
    MasterCategory,
    MonthlyAccountCalculation,
    MonthlyBudget,
    MonthlyBudgetCalculation,
    MonthlySubCategoryBudget,
    MonthlySubCategoryBudgetCalculation,
    Payee,
    PayeeLocation,
    PayeeRenameCondition,
    ScheduledSubtransaction,
    ScheduledTransaction,
    Setting,
    SubCategory,
    Subtransaction,
    Transaction,
    BudgetVersion,
    User,
    UserBudget,
    UserSetting
]


class Tests(unittest.TestCase):
    maxDiff = None

    def testEntityjson(self):
        for t in types:
            obj = t()
            jsonroundtrip = json.loads(json.dumps(obj, cls=ComplexEncoder))
            self.assertEqual(jsonroundtrip, obj.get_dict(convert = True))
            obj2 = t.from_dict(jsonroundtrip)

            self.assertEqual(obj, obj2)

    def testconvertout(self):
        class MyEntity(BudgetEntity,Base):
            amount=Column(Amount())
            date = Column(Date())

        obj=MyEntity()

        result={}
        result['amount'] = 10000
        result['date'] = '2016-10-23'

        result=MyEntity(**MyEntity.convert_out(result))

        self.assertEqual(result.amount,10)
        self.assertEqual(result.date,datetime(2016,10,23).date())

        pass


    def testequality(self):
        tr1 = Transaction(amount=1)
        tr2 = Transaction(amount=2)
        self.assertNotEqual(tr1, tr2)

        tr1 = Transaction(entities_account_id=1)
        tr2 = Transaction(entities_account_id=2)
        self.assertNotEqual(tr1, tr2)

    def test_hash(self):
        tr1 = Transaction()
        tr2 = Transaction()
        self.assertEqual(hash(tr1), hash(tr2))

    def testupdatechangedentities(self):
        obj = Budget()
        assert (obj.be_accounts.track.otherclass == Account)
        assert (len(obj.be_accounts) == 0)
        account = Account()
        changed_entities = dict(
            be_accounts=[account]
        )
        obj.update_from_changed_entities(changed_entities)
        assert (len(obj.be_accounts) == 1)
        assert (next(obj.be_accounts.__iter__()) == account)

    def testappend(self):
        obj = Budget()
        account = Account()
        obj.be_accounts.append(account)
        assert (len(obj.be_accounts) == 1)
        assert (list(obj.be_accounts)[-1] == account)

    def testappendBad(self):
        obj = Budget()
        transaction = Transaction()
        self.assertRaises(ValueError, lambda: obj.be_accounts.append(transaction))

    def test_update_add(self):
        newobject = Account()
        CE = {'be_accounts': [newobject]}
        with session_scope() as session:
            budget = Budget()
            session.add(budget)

        budget.update_from_changed_entities(CE)
        self.assertIn(newobject, budget.be_accounts)

    def test_update_delete(self):
        with session_scope() as session:
            obj = Account()
            budget = Budget()
            budget.be_accounts.append(obj)
            session.add(budget)
            session.commit()

            d=obj.get_dict()

            obj2 = Account.from_dict(d)
            obj2.is_tombstone = True
            CE = {'be_accounts': [obj2]}

            budget.update_from_changed_entities(CE)
            self.assertNotIn(obj, budget.be_accounts)

    def test_update_modify(self):
        obj = Account()
        budget = Budget()
        budget.be_accounts.append(obj)
        budget.be_accounts.track.reset()
        self.assertIn(obj, budget.be_accounts)

        obj.account_name = 'BLA'
        CE = {'be_accounts': [obj]}
        budget.update_from_changed_entities(CE)
        self.assertIn(obj, budget.be_accounts)

    def testCE_nochange(self):
        obj = Budget()
        self.assertEqual(obj.get_changed_entities(), {})

    def testCE_simpleadd(self):
        obj = Budget()
        account = Account()
        obj.be_accounts.append(account)
        self.assertEqual(obj.get_changed_entities(), {'be_accounts': [account]})

    def testCE_replace(self):
        obj = Budget()
        account = Account()
        obj.be_accounts.append(account)
        account2 = Account()
        obj.be_accounts.track.reset()
        obj.be_accounts = [account2]

        changed = obj.get_changed_entities()
        account.is_tombstone = True
        self.assertEqual(list(changed.keys()), ['be_accounts'])
        self.assertEqual(set(changed['be_accounts']), {account, account2})

    def testCE_simpledelete(self):
        obj = Budget()
        account = Account()
        obj.be_accounts.append(account)
        obj.be_accounts.track.reset()
        obj.be_accounts.remove(account)
        account.is_tombstone = True
        self.assertEqual(obj.get_changed_entities(), {'be_accounts': [account]})

    def testCE_simplechange(self):
        obj = Budget()
        account1 = Account()
        obj.be_accounts.append(account1)
        obj.be_accounts.track.reset()
        account1.account_name = 'TEST'
        self.assertEqual(obj.get_changed_entities(), {'be_accounts': [account1]})

    def test_str(self):
        # tests no exceptions when getting the string representation of some entities
        obj = Transaction()
        obj.__str__()

        obj2 = Budget()
        obj2.be_accounts.__str__()

    def jsondefault(self):
        encoded = json.dumps('test', cls=ComplexEncoder)
        self.assertEqual(encoded, 'test')
