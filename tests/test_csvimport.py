# coding=utf-8
import errno
import io
import json
import os
import sys
from datetime import datetime

import configargparse

from common_Live import CommonLive
from pynYNAB.Entity import ComplexEncoder
from pynYNAB.schema.budget import Transaction
from pynYNAB.scripts.csvimport import do_csvimport


class TestCsv(CommonLive):
    def getTr(self, date, payee, amount, memo, account):
        imported_date = datetime.now().date()
        return Transaction(
            entities_account_id=account.id,
            date=date,
            entities_payee_id=self.util_add_payee_by_name_if_doesnt_exist(payee).id,
            imported_payee=payee,
            source='Imported',
            memo=memo,
            amount=amount,
            cash_amount=amount,
            imported_date=imported_date
        )

    def setUp(self):
        super(TestCsv, self).setUp()
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
        self.reload()

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

        accountCredit = self.util_get_empty_account_by_name_if_doesnt_exist('Credit')
        transaction = self.getTr(datetime(year=2016, month=2, day=1).date(), 'Super Pants Inc.', -20, 'Buying pants',
                                 accountCredit)

        for i in range(2):
            do_csvimport(self.args)
            self.reload()

            identical = [tr2 for tr2 in self.client.budget.be_transactions if
                         Transaction.dedupinfo(transaction) == Transaction.dedupinfo(tr2)]
            print('Transactions with same hash: %s' % len(identical))
            self.assertEqual(len(identical), 1)

    def test_duplicateForced(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
"""
        self.writecsv(content)
        accountCash = self.util_get_empty_account_by_name_if_doesnt_exist('Cash')

        transaction = self.getTr(datetime(year=2016, month=2, day=1).date(), 'Super Pants Inc.', -20, 'Buying pants',
                                 accountCash)

        args = self.args
        args.import_duplicates = True

        do_csvimport(args)
        self.reload()
        do_csvimport(args)
        self.reload()
        identical = [tr2 for tr2 in self.client.budget.be_transactions if
                     Transaction.dedupinfo(transaction) == Transaction.dedupinfo(tr2)]
        print('Transactions with same hash: %s' % len(identical))
        self.assertEqual(len(identical), 2)

    def test_import(self):
        content = """Date,Payee,Amount,Memo,Account
2016-02-01,Super Pants Inc.,-20,Buying pants,Cash
2016-02-02,Thai Restaurant,-10,Food,Checking Account
2016-02-02,Chinese Restaurant,-5,Food,Cash
2016-02-03,,10,Saving!,Savings
        """
        self.writecsv(content)
        accountCash = self.util_get_empty_account_by_name_if_doesnt_exist('Cash')
        accountChecking = self.util_get_empty_account_by_name_if_doesnt_exist('Checking Account')
        accountSavings = self.util_get_empty_account_by_name_if_doesnt_exist('Savings')

        Transactions = [
            self.getTr(datetime(year=2016, month=2, day=1).date(), 'Super Pants Inc.', -20, 'Buying pants',
                       accountCash),
            self.getTr(datetime(year=2016, month=2, day=2).date(), 'Thai Restaurant', -10, 'Food', accountChecking),
            self.getTr(datetime(year=2016, month=2, day=2).date(), 'Chinese Restaurant', -5, 'Food', accountCash),
            self.getTr(datetime(year=2016, month=2, day=3).date(), '', 10, 'Saving!', accountSavings),
        ]

        do_csvimport(self.args)
        self.reload()
        for tr in Transactions:
            print(json.dumps(tr, cls=ComplexEncoder))
            print(json.dumps(
                [tr2 for tr2 in self.client.budget.be_transactions if tr2.amount == tr.amount],
                cls=ComplexEncoder))
            self.assertIn(Transaction.dedupinfo(tr), map(Transaction.dedupinfo, self.client.budget.be_transactions))

    def test_encoded(self):
        content = u"""Date,Payee,Amount,Memo,Account
        2016-02-01,Grand Café,-3,Coffee,Cash
                """
        self.writecsv(content, encoding='utf-8')
        accountCash = self.util_get_empty_account_by_name_if_doesnt_exist('Cash')

        Transactions = [
            self.getTr(datetime(year=2016, month=2, day=1).date(), u'Grand Café', -3, 'Coffee',
                       accountCash),
        ]

        do_csvimport(self.args)
        self.reload()
        for tr in Transactions:
            print(json.dumps(tr, cls=ComplexEncoder))
            print(json.dumps(
                [tr2 for tr2 in self.client.budget.be_transactions if tr2.amount == tr.amount],
                cls=ComplexEncoder))
            self.assertIn(Transaction.dedupinfo(tr), list(map(Transaction.dedupinfo,self.client.budget.be_transactions)))
