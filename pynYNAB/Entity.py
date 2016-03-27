import json

from sqlalchemy.exc import InvalidRequestError
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
    logger=get_logger()
    logger.debug('Filtering dict to create %s from dict %s' % (obt, dictionary))
    for key, value in dictionary.items():
        try:
            field = class_mapper(obt.__class__).get_property(key)
        except InvalidRequestError:
            if key in obt.__mapper__.all_orm_descriptors:
                logger.info('ignored a key in an incoming dictionary, most likely a calculated field')
                pass
            else:
                logger.error(
                    'Encountered unknown field %s in a dictionary to create an entity of type %s ' % (key, obj_type))
                logger.error(
                    'Most probably the YNAB API changed, please add that field to the entities schema')
                raise ValueError()
        if isinstance(field, ColumnProperty):
            objdict[key] = value
    logger.debug('Creating a %s from dict %s' % (obt, objdict))
    return obj_type(**objdict)


ignored_fields_for_hash = ['id', 'credit_amount', 'cash_amount']
