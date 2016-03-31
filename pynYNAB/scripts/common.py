from pynYNAB.config import get_logger
from pynYNAB.schema.budget import Payee, SubCategory, MasterCategory, Account

logger = get_logger()


def get_account(client, account_name, create=False):
    try:
        logger.debug('searching for account %s' % account_name)
        return next(a for a in client.budget.be_accounts if a.account_name == account_name)
    except StopIteration:
        if create:
            a = Account(account_name=account_name)
            client.budget.be_accounts.append(a)
            return a
        else:
            logger.error('Couldn''t find this account: %s' % (account_name))
            exit(-1)


def get_payee(client, payee_name, create=False):
    try:
        return next(p for p in client.budget.be_payees if p.name == payee_name)
    except StopIteration:
        if create:
            p=Payee(name=payee_name)
            client.budget.be_payees.append(p)
            return p
        else:
            logger.error('Couldn''t find this payee: %s' % (payee_name))
            exit(-1)


def get_subcategory(client, master_category_name, subcategory_name,create=False):
    try:
        return next(
            s for s in client.budget.be_subcategories
            if s.master_category.name == master_category_name and s.name == subcategory_name)
    except StopIteration:
        if create:
            m = MasterCategory(name=master_category_name)
            s = SubCategory(name=subcategory_name)
            s.master_category = m
            client.budget.be_subcategories.append(s)
            client.budget.be_master_categories.append(m)
            return s
        else:
            logger.error('Couldn''t find this master:subcategory %s:%s'%(master_category_name,subcategory_name))
            exit(-1)


def transaction_dedup(tr):
    return tr.amount, tr.date, tr.entities_account_id, tr.entities_payee_id