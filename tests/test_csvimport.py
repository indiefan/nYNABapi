# coding=utf-8
import errno
import io
import json
import os
import sys
import unittest
from datetime import datetime, date

import configargparse

from pynYNAB.Entity import ComplexEncoder
from pynYNAB.db.db import session_scope
from pynYNAB.schema.budget import Transaction, Account, Payee, MasterCategory, SubCategory
from pynYNAB.scripts.csvimport import transaction_list
from tests.mock import MockClient


class TestCsv(unittest.TestCase):
    def getTr(self, date, payee, amount, memo, account):
        imported_date = datetime.now().date()

        payee = Payee(name=payee)
        self.client.budget.be_payees.append(payee)

        return Transaction(
            entities_account_id=account.id,
            date=date,
            entities_payee_id=payee.id,
            imported_payee=payee,
            source='Imported',
            memo=memo,
            amount=amount,
            cash_amount=amount,
            imported_date=imported_date
        )

    def setUp(self):
        parser = configargparse.getArgumentParser('pynYNAB')
        self.args = parser.parse_known_args()[0]
        self.args.schema = 'example'
        self.args.csvfile = os.path.join('data', 'test.csv')
        self.args.accountname = None
        self.args.import_duplicates = False
        self.args.level = 'debug'

        try:
            os.makedirs(os.path.dirname(self.args.csvfile))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        self.client=MockClient()

    def writecsv(self, content, encoding='utf-8'):
        with io.open(self.args.csvfile, mode='w', encoding=encoding) as f:
            if sys.version[0] == '2':
                f.writelines(unicode(content))
            else:
                f.writelines(content)

    def test_duplicate(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Credit
"""
        self.writecsv(content)

        accountCredit = Account(account_name='Credit')
        self.client.budget.be_accounts.append(accountCredit)
        transaction = self.getTr(date(year=2016, month=2, day=1), 'Super Pants Inc.', -20, 'Buying pants',
                                 accountCredit)

        self.client.budget.be_transactions.append(transaction)

        tr_list = transaction_list(self.args, self.client)

        self.assertEqual(len(tr_list), 0)

    def test_duplicateForced(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
"""
        self.writecsv(content)
        accountCash = Account(account_name='Cash')
        self.client.budget.be_accounts.append(accountCash)

        transaction = self.getTr(date(year=2016, month=2, day=1), 'Super Pants Inc.', -20, 'Buying pants',
                                 accountCash)

        args = self.args
        args.import_duplicates = True

        self.client.budget.be_transactions.append(transaction)

        tr_list = transaction_list(self.args, self.client)

        self.assertEqual(len(tr_list), 1)

    def test_import_categoryschema(self):
        content = """Date,Payee,Category,Memo,Outflow,Inflow
2016-02-01,Super Pants Inc.,MC1:Clothes,Buying Pants,20,0
2016-02-06,Mr Smith,MC2:Rent,"Landlord, Wiring",600,0
        """

        self.args.schema = 'ynab'

        self.writecsv(content)
        self.args.accountname = 'Checking Account'
        accountChecking = Account(account_name='Checking Account')
        self.client.budget.be_accounts.append(accountChecking)

        MC1 = MasterCategory(name='MC1')
        MC2 = MasterCategory(name='MC2')

        self.client.budget.be_master_categories.extend([MC1,MC2])

        clothes = SubCategory(name='Clothes')
        clothes.master_category = MC1
        rent = SubCategory(name='Rent')
        rent.master_category = MC2
        self.client.budget.be_subcategories.extend([clothes, rent])

        tr1 = self.getTr(date(year=2016, month=2, day=1), 'Super Pants Inc.', -20, 'Buying pants',
                         accountChecking)

        tr1.subcategory=clothes

        tr2 = self.getTr(date(year=2016, month=2, day=6), 'Mr Smith', -600, 'Landlord, Wiring', accountChecking)

        tr2.subcategory=rent

        tr_list = transaction_list(self.args, self.client)

        for tr in tr1,tr2:
            print(json.dumps(tr, cls=ComplexEncoder))
            print(json.dumps(
                [trl for trl in tr_list if trl.amount == tr.amount],
                cls=ComplexEncoder))
            self.assertIn(Transaction.dedupinfo(tr), map(Transaction.dedupinfo, tr_list))

    def test_badaccount(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
"""
        self.writecsv(content)
        self.assertRaises(SystemExit,lambda:transaction_list(self.args, self.client))

        def test_badaccount(self):
            content = """Date,Payee,Amount,Memo,Account
    2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
    """
            self.writecsv(content)
            self.assertRaises(SystemExit, lambda: transaction_list(self.args, self.client))

    def test_import(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
2016-02-02,Thai Restaurant,-10,Food,Checking Account
2016-02-02,Chinese Restaurant,-5,Food,Cash
#this line ignored
10/02/2016,Chinese Restaurant,-5,Food,Cash
#previous line invalid cast ignored
2016-02-03,,10,Saving!,Savings
        """
        self.writecsv(content)
        accountCash = Account(account_name='Cash')
        accountChecking = Account(account_name='Checking Account')
        accountSavings = Account(account_name='Savings')
        self.client.budget.be_accounts.append(accountCash)
        self.client.budget.be_accounts.append(accountChecking)
        self.client.budget.be_accounts.append(accountSavings)

        Transactions = [
            self.getTr(datetime(year=2016, month=2, day=1).date(), 'Super Pants Inc.', -20, 'Buying pants',
                       accountCash),
            self.getTr(datetime(year=2016, month=2, day=2).date(), 'Thai Restaurant', -10, 'Food', accountChecking),
            self.getTr(datetime(year=2016, month=2, day=2).date(), 'Chinese Restaurant', -5, 'Food', accountCash),
            self.getTr(datetime(year=2016, month=2, day=3).date(), '', 10, 'Saving!', accountSavings),
        ]

        tr_list = transaction_list(self.args, self.client)

        for tr in Transactions:
            print(json.dumps(tr, cls=ComplexEncoder))
            print(json.dumps(
                [tr2 for tr2 in tr_list if tr2.amount == tr.amount],
                cls=ComplexEncoder))
            self.assertIn(Transaction.dedupinfo(tr), map(Transaction.dedupinfo, tr_list))

    def test_encoded(self):
        content = u"""Date,Payee,Amount,Memo,Account
2016-02-01,Grand Café,-3,Coffee,Cash
"""
        self.writecsv(content, encoding='utf-8')
        accountCash = Account(account_name='Cash')
        self.client.budget.be_accounts.append(accountCash)

        Transactions = [
            self.getTr(datetime(year=2016, month=2, day=1).date(), u'Grand Café', -3, 'Coffee',
                       accountCash),
        ]

        tr_list = transaction_list(self.args, self.client)

        for tr in Transactions:
            print(json.dumps(tr, cls=ComplexEncoder))
            print(json.dumps(
                [tr2 for tr2 in tr_list if tr2.amount == tr.amount],
                cls=ComplexEncoder))
            self.assertIn(Transaction.dedupinfo(tr), list(map(Transaction.dedupinfo, tr_list)))
