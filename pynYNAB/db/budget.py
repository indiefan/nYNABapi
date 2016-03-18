from sqlalchemy import Column
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Date,Boolean,String,Enum,Integer
from sqlalchemy.schema import ForeignKey

from pynYNAB.db import Base
from pynYNAB.db.Entity import Entity
from pynYNAB.db.Types import Amount, Dates, GUID
from pynYNAB.schema.enums import AccountTypes, Sources


class Transaction(Entity,Base):
    accepted = Column(Boolean())
    # amount = Column(Amount())
    cash_amount = Column(Amount())
    check_number = Column(String())
    cleared = Column(String(),default='Uncleared')
    # credit_amount = Column(Amount(),default=0)
    date = Column(Date())
    date_entered_from_schedule = Column(Date())
    entities_account_id = Column(GUID(),ForeignKey('Account'))
    entities_payee_id = Column(String(36),ForeignKey('Payee'))
    entities_scheduled_transaction_id = Column(String(36),ForeignKey('ScheduledTransaction'))
    entities_subcategory_id = Column(String(36),ForeignKey('Subcategory'))
    flag = Column(String())
    imported_date = Column(Date())
    imported_payee = Column(String())
    matched_transaction_id = Column(String(36),ForeignKey('Transaction'))
    memo = Column(String())
    # source = Column(Enum(Sources))
    # transfer_account_id = Column(GUID(),ForeignKey('Account'))
    # transfer_subtransaction_id = Column(GUID(),ForeignKey('Subtransaction'))
    # transfer_transaction_id = Column(GUID(),ForeignKey('Transaction'))
    ynab_id = Column(String())


class MasterCategory(Entity,Base):
    deletable = Column(Boolean(),default=True)
    internal_name = Column(String())
    is_hidden = Column(Boolean(),default=False)
    name = Column(String())
    note = Column(String())
    sortable_index = Column(Integer())


class Setting(Entity,Base):
    setting_name = Column(String())
    setting_value = Column(String())


class MonthlyBudgetCalculation(Entity,Base):
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


class AccountMapping(Entity,Base):
    date_sequence = Column(Date())
    entities_account_id = Column(String())
    hash = Column(String())
    fid = Column(String())
    salt = Column(String())
    shortened_account_id = Column(String())
    should_flip_payees_memos = Column(String())
    should_import_memos = Column(String())
    skip_import = Column(String())


class Subtransaction(Entity,Base):
    amount = Column(Amount())
    cash_amount = Column(Amount())
    check_number = Column(String())
    credit_amount = Column(Amount())
    entities_payee_id = Column(String())
    entities_subcategory_id = Column(String())
    entities_transaction_id = Column(String())
    memo = Column(String())
    sortable_index = Column(Integer())
    transfer_account_id = Column(String())
    transfer_transaction_id = Column(String())


class ScheduledSubtransaction(Entity,Base):
    amount = Column(Amount())
    entities_payee_id = Column(String())
    entities_scheduled_transaction_id = Column(String())
    entities_subcategory_id = Column(String())
    memo = Column(String())
    sortable_index = Column(Integer())
    transfer_account_id = Column(String())


class MonthlyBudget(Entity,Base):
    month = Column(String())
    note = Column(String())


class Subcategory(Entity,Base):
    entities_account_id = Column(String())
    entities_master_category_id = Column(String())
    goal_creation_month = Column(String())
    goal_type = Column(String())
    internal_name = Column(String())
    is_hidden = Column(Boolean(),default=False)
    monthly_funding = Column(String())
    name = Column(String())
    note = Column(String())
    sortable_index = Column(Integer())
    target_balance = Column(Amount())
    target_balance_month = Column(String())
    type = Column(String())


class PayeeLocation(Entity,Base):
    entities_payee_id = Column(String())
    latitude = Column(String())
    longitude = Column(String())


class AccountCalculation(Entity,Base):
    cleared_balance = Column(Amount())
    entities_account_id = Column(String())
    error_count = Column(String())
    info_count = Column(String())
    transaction_count = Column(String())
    uncleared_balance = Column(Amount())
    warning_count = Column(String())


class MonthlyAccountCalculation(Entity,Base):
    cleared_balance = Column(Amount())
    entities_account_id = Column(String())
    error_count = Column(String())
    info_count = Column(String())
    month = Column(String())
    transaction_count = Column(String())
    uncleared_balance = Column(Amount())
    warning_count = Column(String())


class MonthlySubcategoryBudgetCalculation(Entity,Base):
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


class ScheduledTransaction(Entity,Base):
    amount = Column(Amount())
    date = Column(Date())
    entities_account_id = Column(String(36),ForeignKey('Account'))
    entities_payee_id = Column(String(36),ForeignKey('Payee'))
    entities_subcategory_id = Column(String(36),ForeignKey('Subcategory'))
    flag = Column(String(),default='')
    frequency = Column(String())
    memo = Column(String())
    transfer_account_id = Column(String())
    upcoming_instances = Column(Dates())


class Payee(Entity,Base):
    auto_fill_amount = Column(Amount())
    auto_fill_amount_enabled = Column(String())
    auto_fill_memo = Column(String())
    auto_fill_memo_enabled = Column(String())
    auto_fill_subcategory_enabled = Column(String())
    auto_fill_subcategory_id = Column(String())
    enabled = Column(Boolean(),default=True)
    entities_account_id = Column(String())
    internal_name = Column(String())
    name = Column(String())
    rename_on_import_enabled = Column(String())


class MonthlySubcategoryBudget(Entity,Base):
    budgeted = Column(Amount())
    entities_monthly_budget_id = Column(String())
    entities_subcategory_id = Column(String())
    note = Column(String())
    overspending_handling = Column(String())


class TransactionGroup(Entity,Base):
    be_transaction = Column(String())
    be_subtransactions = Column(String())
    be_matched_transaction = Column(String())


class PayeeRenameCondition(Entity,Base):
    entities_payee_id = Column(String(36),ForeignKey('Payee'))
    operand = Column(String())
    operator = Column(String())


class Account(Entity,Base):
    account_name = Column(String())
    account_type = Column(Enum(AccountTypes))
    direct_connect_account_id = Column(String())
    direct_connect_enabled = Column(Boolean(),default=False)
    direct_connect_institution_id = Column(String())
    hidden = Column(Boolean(),default=False)
    last_entered_check_number = Column(String())
    last_imported_at = Column(String())
    last_imported_error_code = Column(String())
    last_reconciled_balance = Column(String())
    last_reconciled_date = Column(Date())
    note = Column(String())
    sortable_index = Column(Integer())
    on_budget = Column(Boolean())
