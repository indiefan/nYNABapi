import random

from sqlalchemy import Column as OriginalColumn
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Date, Boolean, String, Enum, Integer

from pynYNAB.Entity import on_budget_dict
from pynYNAB.db import Base
from pynYNAB.db.Entity import Entity, Column, EntityBase
from pynYNAB.db.Types import Amount, IgnorableString, IgnorableBoolean
from pynYNAB.db.Types import Dates
from pynYNAB.roots import Root, ListOfEntities
from pynYNAB.schema.enums import AccountTypes, Sources


class Budget(Root, Base):
    OPNAME = 'syncBudgetData'

    def __init__(self):
        super(Budget, self).__init__()
        self.budget_version_id = None

    be_transactions = ListOfEntities("Transaction")
    be_master_categories = ListOfEntities('MasterCategory')
    be_settings = ListOfEntities('Setting')
    be_monthly_budget_calculations = ListOfEntities('MonthlyBudgetCalculation')
    be_account_mappings = ListOfEntities('AccountMapping')
    be_subtransactions = ListOfEntities('Subtransaction')
    be_scheduled_subtransactions = ListOfEntities('ScheduledSubtransaction')
    be_monthly_budgets = ListOfEntities('MonthlyBudget')
    be_subcategories = ListOfEntities('Subcategory')
    be_payee_locations = ListOfEntities('PayeeLocation')
    be_account_calculations = ListOfEntities('AccountCalculation')
    be_monthly_account_calculations = ListOfEntities('MonthlyAccountCalculation')
    be_monthly_subcategory_budget_calculations = ListOfEntities('MonthlySubcategoryBudgetCalculation')
    be_scheduled_transactions = ListOfEntities('ScheduledTransaction')
    be_payees = ListOfEntities('Payee')
    be_monthly_subcategory_budgets = ListOfEntities('MonthlySubcategoryBudget')
    be_payee_rename_conditions = ListOfEntities('PayeeRenameCondition')
    be_accounts = ListOfEntities('Account')
    last_month = Column(Date())
    first_month = Column(Date())

    def get_request_data(self):
        k, request_data = super(Budget, self).get_request_data()
        request_data['budget_version_id'] = self.budget_version_id
        request_data['calculated_entities_included'] = False
        return k, request_data

    def get_changed_entities(self):
        changed_entities = super(Budget, self).get_changed_entities()
        if 'be_transactions' in changed_entities:
            changed_entities['be_transaction_groups'] = []
            for tr in changed_entities.pop('be_transactions'):
                subtransactions = []
                if 'be_subtransactions' in changed_entities:
                    for subtr in [subtransaction for subtransaction in changed_entities.get('be_subtransactions') if
                                  subtransaction.entities_transaction_id == tr.id]:
                        changed_entities['be_subtransactions'].remove(subtr)
                        subtransactions.append(subtr)
                changed_entities['be_transaction_groups'].append(TransactionGroup(
                    id=tr.id,
                    be_transaction=tr,
                    be_subtransactions=subtransactions
                ))
        if changed_entities.get('be_subtransactions') is not None:
            del changed_entities['be_subtransactions']
        return changed_entities


class BudgetEntity(Entity):
    @declared_attr
    def budget_id(self):
        return OriginalColumn(String(36), ForeignKey('budget.id'))

    @declared_attr
    def budget(self):
        return relationship("Budget")


class Transaction(BudgetEntity, Base):
    accepted = Column(Boolean(), default=True, nullable=False)
    amount = Column(Amount(), default=0)
    cash_amount = Column(Amount(), default=0)
    check_number = Column(String())
    cleared = Column(String(), default='Uncleared')
    credit_amount = Column(Amount(), default=0)
    date = Column(Date())
    date_entered_from_schedule = Column(Date())
    entities_account_id = Column(String(36), ForeignKey('account.id'))
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    entities_scheduled_transaction_id = Column(String(36), ForeignKey('scheduledtransaction.id'))
    entities_subcategory_id = Column(String(36), ForeignKey('subcategory.id'))
    flag = Column(String())
    imported_date = Column(Date())
    imported_payee = Column(String())
    matched_transaction_id = Column(String(36), ForeignKey('transaction.id'))
    memo = Column(String())
    source = Column(Enum(*Sources.__members__.keys(), name='Sources'))
    transfer_account_id = Column(String(36), ForeignKey('account.id'))
    transfer_subtransaction_id = Column(String(36), ForeignKey('subtransaction.id'))
    transfer_transaction_id = Column(String(36), ForeignKey('transaction.id'))
    ynab_id = Column(String())

    @classmethod
    def dedupinfo(cls, row):
        return row.amount, row.date, row.entities_account_id, row.entities_payee_id


class MasterCategory(BudgetEntity, Base):
    deletable = Column(Boolean(), default=True)
    internal_name = Column(String())
    is_hidden = Column(Boolean(), default=False)
    name = Column(String())
    note = Column(String())
    sortable_index = Column(Integer())


class Setting(BudgetEntity, Base):
    setting_name = Column(String())
    setting_value = Column(String())


class MonthlyBudgetCalculation(BudgetEntity, Base):
    additional_to_be_budgeted = Column(Amount())
    age_of_money = Column(String())
    available_to_budget = Column(String())
    balance = Column(String())
    budgeted = Column(String())
    calculation_notes = Column(String())
    cash_outflows = Column(Amount())
    credit_outflows = Column(Amount())
    deferred_income = Column(Amount())
    entities_monthly_budget_id = Column(String())
    hidden_balance = Column(Amount())
    hidden_budgeted = Column(Amount())
    hidden_cash_outflows = Column(Amount())
    hidden_credit_outflows = Column(Amount())
    immediate_income = Column(Amount())
    over_spent = Column(Amount())
    previous_income = Column(Amount())
    uncategorized_balance = Column(Amount())
    uncategorized_cash_outflows = Column(Amount())
    uncategorized_credit_outflows = Column(Amount())


class AccountMapping(BudgetEntity, Base):
    date_sequence = Column(Date())
    entities_account_id = Column(String(36), ForeignKey('account.id'))
    hash = Column(String())
    fid = Column(String())
    salt = Column(String())
    shortened_account_id = Column(String())
    should_flip_payees_memos = Column(String())
    should_import_memos = Column(String())
    skip_import = Column(String())


class Subtransaction(BudgetEntity, Base):
    amount = Column(Amount())
    cash_amount = Column(Amount())
    check_number = Column(String())
    credit_amount = Column(Amount())
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    entities_subcategory_id = Column(String(36), ForeignKey('subcategory.id'))
    entities_transaction_id = Column(String(36), ForeignKey('transaction.id'))
    memo = Column(String())
    sortable_index = Column(Integer())
    transfer_account_id = Column(String(36), ForeignKey('account.id'))
    transfer_transaction_id = Column(String(36), ForeignKey('transaction.id'))


class ScheduledSubtransaction(BudgetEntity, Base):
    amount = Column(Amount())
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    entities_scheduled_transaction_id = Column(String(36), ForeignKey('scheduledtransaction.id'))
    entities_subcategory_id = Column(String(36), ForeignKey('subcategory.id'))
    memo = Column(String())
    sortable_index = Column(Integer())
    transfer_account_id = Column(String(36), ForeignKey('account.id'))


class MonthlyBudget(BudgetEntity, Base):
    month = Column(String())
    note = Column(String())


class Subcategory(BudgetEntity, Base):
    entities_account_id = Column(String(36), ForeignKey('account.id'))
    entities_master_category_id = Column(String(36), ForeignKey('mastercategory.id'))
    goal_creation_month = Column(String())
    goal_type = Column(String())
    internal_name = Column(String())
    is_hidden = Column(Boolean(), default=False)
    monthly_funding = Column(String())
    name = Column(String())
    note = Column(String())
    sortable_index = Column(Integer())
    target_balance = Column(Amount())
    target_balance_month = Column(String())
    type = Column(String())


class PayeeLocation(BudgetEntity, Base):
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    latitude = Column(String())
    longitude = Column(String())


class AccountCalculation(BudgetEntity, Base):
    cleared_balance = Column(Amount())
    entities_account_id = Column(String(36), ForeignKey('account.id'))
    error_count = Column(String())
    info_count = Column(String())
    transaction_count = Column(String())
    uncleared_balance = Column(Amount())
    warning_count = Column(String())


class MonthlyAccountCalculation(BudgetEntity, Base):
    cleared_balance = Column(Amount())
    entities_account_id = Column(String())
    error_count = Column(String())
    info_count = Column(String())
    month = Column(String())
    transaction_count = Column(String())
    uncleared_balance = Column(Amount())
    warning_count = Column(String())


class MonthlySubcategoryBudgetCalculation(BudgetEntity, Base):
    all_spending = Column(Amount())
    all_spending_since_last_payment = Column(Amount())
    balance = Column(Amount())
    balance_previous_month = Column(Amount())
    budgeted_average = Column(Amount())
    budgeted_cash_outflows = Column(Amount())
    budgeted_credit_outflows = Column(Amount())
    budgeted_previous_month = Column(Amount())
    budgeted_spending = Column(Amount())
    cash_outflows = Column(Amount())
    credit_outflows = Column(Amount())
    entities_monthly_subcategory_budget_id = Column(String())
    goal_expected_completion = Column(String())
    goal_overall_funded = Column(Amount())
    goal_overall_left = Column(Amount())
    goal_target = Column(String())
    goal_under_funded = Column(String())
    overspending_affects_buffer = Column(String())
    payment_average = Column(Amount())
    payment_previous_month = Column(Amount())
    spent_average = Column(Amount())
    spent_previous_month = Column(Amount())
    unbudgeted_cash_outflows = Column(Amount())
    unbudgeted_credit_outflows = Column(Amount())
    upcoming_transactions = Column(Amount())
    positive_cash_outflows = Column(Amount())


class ScheduledTransaction(BudgetEntity, Base):
    amount = Column(Amount())
    date = Column(Date())
    entities_account_id = Column(String(36), ForeignKey('account.id'))
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    entities_subcategory_id = Column(String(36), ForeignKey('subcategory.id'))
    flag = Column(String(), default='')
    frequency = Column(String())
    memo = Column(String())
    transfer_account_id = Column(String())
    upcoming_instances = Column(Dates())


class Payee(BudgetEntity, Base):
    auto_fill_amount = Column(Amount())
    auto_fill_amount_enabled = Column(String())
    auto_fill_memo = Column(String())
    auto_fill_memo_enabled = Column(String())
    auto_fill_subcategory_enabled = Column(String())
    auto_fill_subcategory_id = Column(String(36), ForeignKey('subcategory.id'))
    enabled = Column(Boolean(), default=True)
    entities_account_id = Column(String())
    internal_name = Column(String())
    name = Column(String())
    rename_on_import_enabled = Column(String())


class MonthlySubcategoryBudget(BudgetEntity, Base):
    budgeted = Column(Amount())
    entities_monthly_budget_id = Column(String())
    entities_subcategory_id = Column(String())
    note = Column(String())
    overspending_handling = Column(String())


class TransactionGroup(EntityBase, Base):
    be_transaction = Column(String())
    be_subtransactions = Column(String())
    be_matched_transaction = Column(String())


class PayeeRenameCondition(BudgetEntity, Base):
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    operand = Column(String())
    operator = Column(String())


class Account(BudgetEntity, Base):
    account_name = Column(String())
    account_type = Column(Enum(*AccountTypes.__members__.keys(), name='AccountTypes'))
    direct_connect_account_id = Column(IgnorableString())
    direct_connect_enabled = Column(IgnorableBoolean(), default=False)
    direct_connect_institution_id = Column(IgnorableString())
    hidden = Column(Boolean(), default=False)
    last_entered_check_number = Column(String())
    last_imported_at = Column(IgnorableString())
    last_imported_error_code = Column(IgnorableString())
    last_reconciled_balance = Column(String())
    last_reconciled_date = Column(Date())
    note = Column(String())
    sortable_index = Column(Integer(), default=lambda: random.randint(1, 10000))

    @hybrid_property
    def on_budget(self):
        return on_budget_dict[self.account_type.value] if self.account_type else None
