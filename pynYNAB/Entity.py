import json
from sqlalchemy.orm import class_mapper, ColumnProperty

from pynYNAB.db.Entity import EntityBase
from pynYNAB.config import get_logger


def undef():
    pass


on_budget_dict = dict(
    undef=None,
    Checking=True,
    Savings=True,
    CreditCard=True,
    Cash=True,
    LineOfCredit=True,
    Paypal=True,
    MerchantAccount=True,
    InvestmentAccount=False,
    Mortgage=False,
    OtherAsset=False,
    OtherLiability=False,
)
on_budget_dict[None] = None


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, EntityBase):
            return obj.getdict()
        elif obj == undef:
            return
        else:
            return json.JSONEncoder.default(self, obj)


def obj_from_dict(obj_type, dictionary):
    objdict = {}
    obt = obj_type()
    for key, value in dictionary.items():
        try:
            field = class_mapper(obt.__class__).get_property(key)
        except KeyError:
            get_logger().error('Encountered field %s in a dictionary to create an entity of type %s ' % (key, obj_type))
            raise ValueError()
        if isinstance(field, ColumnProperty):
            objdict[key] = value

    return obj_type(**objdict)


ignored_fields_for_hash = ['id', 'credit_amount', 'cash_amount']
