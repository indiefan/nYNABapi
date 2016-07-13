import os
import unittest
from datetime import datetime

from pynYNAB.schema.budget import Transaction, Account, Payee
from pynYNAB.app.scripts.ofximport import transaction_list
from tests.common_test import commonTestCaseBase
from tests.mock import MockClient


class thing():
    pass


class TestOFX(commonTestCaseBase):
    content = """OFXHEADER:100
    DATA:OFXSGML
    VERSION:102
    SECURITY:NONE
    ENCODING:USASCII
    CHARSET:1252
    COMPRESSION:NONE
    OLDFILEUID:NONE
    NEWFILEUID:NONE
    <OFX>
    <SIGNONMSGSRSV1>
    <SONRS>
    <STATUS>
    <CODE>0
    <SEVERITY>INFO
    </STATUS>
    <DTSERVER>20130313133728
    <LANGUAGE>FRA
    </SONRS>
    </SIGNONMSGSRSV1>
    <BANKMSGSRSV1>
    <STMTTRNRS>
    <TRNUID>29939615002
    <STATUS>
    <CODE>0
    <SEVERITY>INFO
    </STATUS>
    <STMTRS>
    <CURDEF>EUR
    <BANKACCTFROM>
    <BANKID>11706
    <BRANCHID>41029
    <ACCTID>29939615002
    <ACCTTYPE>CHECKING
    </BANKACCTFROM>
    <BANKTRANLIST>
    <DTSTART>20130128000000
    <DTEND>20130314235959
    <STMTTRN>
    <TRNTYPE>CHECK
    <DTPOSTED>20130312
    <TRNAMT>-491.09
    <FITID>13071099780237330004
    <CHECKNUM>0003445
    <NAME>CHEQUE
    <MEMO>CHEQUE
    </STMTTRN>
    </BANKTRANLIST>
    <LEDGERBAL>
    <BALAMT>-6348.01
    <DTASOF>20130312
    </LEDGERBAL>
    <AVAILBAL>
    <BALAMT>-6348.01
    <DTASOF>20130312
    </AVAILBAL>
    </STMTRS>
    </STMTTRNRS>
    </BANKMSGSRSV1>
    </OFX>"""

    def setUp(self):
        self.args = thing()
        self.args.ofxfile = os.path.join('data', 'test.ofx')
        with open(self.args.ofxfile, mode='w') as f:
            f.writelines(self.content)

        self.client = MockClient()

        key = '11706 41029 29939615002'
        account = Account(account_name='TEST', note='great note key[%s]key' % key)
        self.client.budget.be_accounts.append(account)

        payee = Payee(name='CHEQUE')
        self.client.budget.be_payees.append(payee)

        self.Transactions = [
            self.get_transaction(datetime(year=2013, month=3, day=12).date(), payee, -491.09,
                                 'CHEQUE    13071099780237330004', account),
        ]

    def get_transaction(self,date, payee, amount, memo, account_obj):
        return Transaction(
            entities_account_id=account_obj.id,
            date=date,
            entities_payee_id=payee.id,
            imported_payee=payee.name,
            source='Imported',
            check_number='0003445',
            memo=memo,
            amount=amount,
            imported_date=datetime.now().date()
        )

    def test_ofximport(self):
        tr_list = transaction_list(self.args, self.client)
        self.assertEqual(len(tr_list),1)
        for tr in self.Transactions:
            self.assertIn(tr, tr_list)

    def test_duplicate(self):
        self.client.budget.be_transactions.extend(self.Transactions)
        tr_list = transaction_list(self.args, self.client)
        self.assertEqual(len(tr_list),0)

