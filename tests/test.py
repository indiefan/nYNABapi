import json
import sys
import unittest
from datetime import datetime

from sqlalchemy import Date
from sqlalchemy import create_engine

from pynYNAB.Entity import Column
from pynYNAB.Types import Amount
from pynYNAB.connection import ComplexEncoder
from pynYNAB.db import Base, session_scope, session_factory, Session
from pynYNAB.schema.budget import Account, AccountCalculation, AccountMapping, MasterCategory, Transaction, SubCategory, \
    MonthlyAccountCalculation, MonthlyBudget, MonthlySubCategoryBudget, MonthlyBudgetCalculation, \
    MonthlySubCategoryBudgetCalculation, PayeeLocation, Payee, PayeeRenameCondition, ScheduledSubtransaction, \
    ScheduledTransaction, Setting, Subtransaction, Budget, BudgetEntity
from pynYNAB.schema.catalog import BudgetVersion, User, UserBudget, UserSetting
from pynYNAB.track import reset_track
from tests.common_test import commonTestCaseBase

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


class Tests(commonTestCaseBase):
    maxDiff = None


    def collectionsEqualIgnoreOrder(self, expected_seq, actual_seq, msg=None):
        if sys.version_info[0] == '2':
            return self.assertItemsEqual(expected_seq,actual_seq,msg)
        if sys.version_info[0] == '3':
            return self.assertCountEqual(expected_seq, actual_seq, msg)

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
        budget = Budget()

        budget.update_from_changed_entities(CE)
        self.assertIn(newobject, budget.be_accounts)

    def test_update_delete(self):
        obj = Account()
        budget = Budget()
        budget.be_accounts.append(obj)

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
        reset_track(budget)
        self.assertIn(obj, budget.be_accounts)

        obj.account_name = 'BLA'
        CE = {'be_accounts': [obj]}
        budget.update_from_changed_entities(CE)
        self.assertIn(obj, budget.be_accounts)

    def testCE_nochange(self):
        obj = Budget()
        changed=obj.get_changed_entities()
        self.assertEqual(changed, {})

    def testCE_simpleadd(self):
        obj = Budget()
        account = Account()
        obj.be_accounts.append(account)
        changed = obj.get_changed_entities()
        self.collectionsEqualIgnoreOrder(list(changed.keys()), ['be_accounts'])
        self.collectionsEqualIgnoreOrder(changed['be_accounts'], [account])

    def testCE_replace(self):
        obj = Budget()
        account = Account(account_name='account')
        obj.be_accounts.append(account)
        reset_track(obj)
        account2 = Account(account_name='account2')
        print('RESET TRACK')
        print('obj id %s'%obj.id)
        obj.be_accounts = [account2]

        changed = obj.get_changed_entities()
        #caccount=account.copy()
        #caccount.is_tombstone = True
        self.collectionsEqualIgnoreOrder(list(changed.keys()), ['be_accounts'])
        self.collectionsEqualIgnoreOrder(changed['be_accounts'], [account, account2])

    def testCE_simpledelete(self):
        obj = Budget()
        account = Account()
        obj.be_accounts.append(account)
        reset_track(obj)
        obj.be_accounts.remove(account)
        account.is_tombstone = True

        changed = obj.get_changed_entities()
        self.collectionsEqualIgnoreOrder(list(changed.keys()), ['be_accounts'])
        self.collectionsEqualIgnoreOrder([account], changed['be_accounts'])

    def testCE_simplechange(self):
        obj = Budget()
        account1 = Account()
        obj.be_accounts.append(account1)
        reset_track(obj)
        account1.account_name = 'TEST'
        changed=obj.get_changed_entities()
        self.collectionsEqualIgnoreOrder(list(changed.keys()), ['be_accounts'])
        self.collectionsEqualIgnoreOrder(changed['be_accounts'], [account1])

    def test_str(self):
        # tests no exceptions when getting the string representation of some entities
        obj = Transaction()
        obj.__str__()

        obj2 = Budget()
        obj2.be_accounts.__str__()

    def jsondefault(self):
        encoded = json.dumps('test', cls=ComplexEncoder)
        self.assertEqual(encoded, 'test')
