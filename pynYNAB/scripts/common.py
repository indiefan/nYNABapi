from pynYNAB.config import get_logger
from pynYNAB.schema.budget import Payee

logger = get_logger()


def get_account(client, account_name):
    try:
        logger.debug('searching for account %s' % account_name)
        return next(a for a in client.budget.be_accounts if a.account_name == account_name)
    except StopIteration:
        logger.error('Couldn''t find this account: %s' % account_name)
        exit(-1)


def get_payee(client, payee_name):
    try:
        return next(p for p in client.budget.be_payees if p.name == payee_name)
    except StopIteration:
        return Payee(name=payee_name)


def get_subcategory(client, subcategory_name):
    try:
        return next(
            s for s in client.budget.be_subcategories if s.master_category.name + ':' + s.name == subcategory_name)
    except StopIteration:
        return Payee(name=subcategory_name)
