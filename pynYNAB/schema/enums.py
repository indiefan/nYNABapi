import sqlalchemy
from enum import Enum
from sqlalchemy import types


class AccountTypes(Enum):
    undef = 'undef'
    Checking = 'Checking'
    Savings = 'Savings'
    CreditCard = 'CreditCard'
    Cash = 'Cash'
    LineOfCredit = 'LineOfCredit'
    Paypal = 'Paypal'
    MerchantAccount = 'MerchantAccount'
    InvestmentAccount = 'InvestmentAccount'
    Mortgage = 'Mortgage'
    OtherAsset = 'OtherAsset'
    OtherLiability = 'OtherLiability'


class Sources(Enum):
    Scheduler = "Scheduler"
    Imported = "Imported"
    Matched = "Matched"



class MyEnumType(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.SmallInteger

    def __init__(self, values):
        sqlalchemy.types.TypeDecorator.__init__(self)
        self.values = values

    def process_bind_param(self, value, dialect):
        return None if value is None else getattr(self.values,value).name

    def process_result_value(self, value, dialect):
        return None if value is None else self.values[value]
