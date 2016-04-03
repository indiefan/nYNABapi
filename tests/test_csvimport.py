# coding=utf-8
import errno
import io
import json
import os
import sys
import unittest
from datetime import datetime, date

import configargparse

from pynYNAB.connection import ComplexEncoder
from pynYNAB.schema.budget import Transaction
from pynYNAB.scripts.common import get_payee, get_account, get_subcategory
from pynYNAB.scripts.csvimport import transaction_list, transaction_dedup
from tests.mock import MockClient


class TestCsv(unittest.TestCase):
    def getTr(self, date, payee_name, amount, memo, account_name):
        imported_date = datetime.now().date()

        payee = get_payee(self.client, payee_name, create=True)
        account = get_account(self.client, account_name, create=True)

        return Transaction(
            entities_account_id=account.id,
            date=date,
            entities_payee_id=payee.id,
            imported_payee=payee,
            source='Imported',
            memo=memo,
            amount=amount,
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
        self.args.encoding = 'utf-8'

        try:
            os.makedirs(os.path.dirname(self.args.csvfile))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        self.client = MockClient()

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

        transaction = self.getTr(date(year=2016, month=2, day=1), 'Super Pants Inc.', -20, 'Buying pants',
                                 'Credit')

        self.client.budget.be_transactions.append(transaction)

        tr_list = transaction_list(self.args, self.client)

        self.assertEqual(len(tr_list), 0)

    def test_duplicateForced(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
"""
        self.writecsv(content)

        transaction = self.getTr(date(year=2016, month=2, day=1), 'Super Pants Inc.', -20, 'Buying pants',
                                 'Cash')

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
        self.args.accountname = 'Checking Account'

        self.writecsv(content)

        clothes = get_subcategory(self.client, 'MC1', 'Clothes', create=True)
        rent = get_subcategory(self.client, 'MC2', 'Rent', create=True)

        tr1 = self.getTr(date(year=2016, month=2, day=1), 'Super Pants Inc.', -20, 'Buying pants',
                         'Checking Account')

        tr1.subcategory = clothes

        tr2 = self.getTr(date(year=2016, month=2, day=6), 'Mr Smith', -600, 'Landlord, Wiring', 'Checking Account')

        tr2.subcategory = rent

        tr_list = transaction_list(self.args, self.client)

        for tr in tr1, tr2:
            self.assertIn(transaction_dedup(tr), map(transaction_dedup,tr_list))

    def test_inexistent_account(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
"""
        self.writecsv(content)

        self.client.budget.be_accounts.remove(get_account(self.client, 'Cash', create=True))
        self.assertRaises(SystemExit, lambda: transaction_list(self.args, self.client))

    def test_inexistent_payee(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
"""
        self.writecsv(content)

        self.client.budget.be_payees.remove(get_payee(self.client, 'Super Pants Inc.', create=True))
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

        Transactions = [
            self.getTr(datetime(year=2016, month=2, day=1).date(), 'Super Pants Inc.', -20, 'Buying pants',
                       'Cash'),
            self.getTr(datetime(year=2016, month=2, day=2).date(), 'Thai Restaurant', -10, 'Food', 'Checking Account'),
            self.getTr(datetime(year=2016, month=2, day=2).date(), 'Chinese Restaurant', -5, 'Food', 'Cash'),
            self.getTr(datetime(year=2016, month=2, day=3).date(), '', 10, 'Saving!', 'Savings'),
        ]

        tr_list = transaction_list(self.args, self.client)

        for tr in Transactions:
            print(json.dumps(tr, cls=ComplexEncoder))
            print(json.dumps(
                [tr2 for tr2 in tr_list if tr2.amount == tr.amount],
                cls=ComplexEncoder))
            self.assertIn(transaction_dedup(tr), map(transaction_dedup, tr_list))

    def test_encoded(self):
        content = u"""Date,Payee,Amount,Memo,Account
2016-02-01,Grand Café,-3,Coffee,Cash
"""
        self.writecsv(content, encoding='iso-8859-1')
        self.args.encoding = 'iso-8859-1'

        Transactions = {
            self.getTr(datetime(year=2016, month=2, day=1).date(), u'Grand Café', -3, 'Coffee',
                       'Cash'),
        }

        tr_list = transaction_list(self.args, self.client)

        for tr in Transactions:
            print(json.dumps(tr, cls=ComplexEncoder))
            print(json.dumps(
                [tr2 for tr2 in tr_list if tr2.amount == tr.amount],
                cls=ComplexEncoder))
            self.assertIn(transaction_dedup(tr), list(map(transaction_dedup, tr_list)))
