import random

from datetime import datetime, date
from sqlalchemy import Column as OriginalColumn
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship,validates
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Date, Boolean, String, Enum, Integer

from pynYNAB.db import Base
from pynYNAB.db.Entity import Entity, Column, EntityBase
from pynYNAB.db.Types import Amount, IgnorableString, IgnorableBoolean, Amounthybrid
from pynYNAB.db.Types import Dates
from pynYNAB.roots import Root, ListOfEntities
from pynYNAB.schema.catalog import BudgetVersion
from pynYNAB.schema.enums import AccountTypes, Sources, MyEnumType


class Budget(Root, Base):
    OPNAME = 'syncBudgetData'

    be_transactions = ListOfEntities("Transaction")
    be_master_categories = ListOfEntities('MasterCategory')
    be_settings = ListOfEntities('Setting')
    be_monthly_budget_calculations = ListOfEntities('MonthlyBudgetCalculation')
    be_account_mappings = ListOfEntities('AccountMapping')
    be_subtransactions = ListOfEntities('Subtransaction')
    be_scheduled_subtransactions = ListOfEntities('ScheduledSubtransaction')
    be_monthly_budgets = ListOfEntities('MonthlyBudget')
    be_subcategories = ListOfEntities('SubCategory')
    be_payee_locations = ListOfEntities('PayeeLocation')
    be_account_calculations = ListOfEntities('AccountCalculation')
    be_monthly_account_calculations = ListOfEntities('MonthlyAccountCalculation')
    be_monthly_subcategory_budget_calculations = ListOfEntities('MonthlySubCategoryBudgetCalculation')
    be_scheduled_transactions = ListOfEntities('ScheduledTransaction')
    be_payees = ListOfEntities('Payee')
    be_monthly_subcategory_budgets = ListOfEntities('MonthlySubCategoryBudget')
    be_payee_rename_conditions = ListOfEntities('PayeeRenameCondition')
    be_accounts = ListOfEntities('Account')
    last_month = Column(Date())
    first_month = Column(Date())

    budget_version_id = Column(String(36),ForeignKey('budgetversion.id'))
    budget_version = relationship(BudgetVersion)

    track_id = Column(String, ForeignKey('budget.id'))
    track = relationship('Budget',uselist=False)

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
    def parent(self):
        return relationship("Budget")


class Transaction(BudgetEntity, Base):
    accepted = Column(Boolean(), default=True, nullable=False)
    amount = Column(Amount(), default=0)

    @Amounthybrid
    def cash_amount(self):
        if self.account and self.account.account_type != AccountTypes.CreditCard:
            return self.amount
        return 0

    @Amounthybrid
    def credit_amount(self):
        if self.account and self.account.account_type == AccountTypes.CreditCard:
            return self.amount
        return 0

    check_number = Column(String())
    cleared = Column(String(), default='Uncleared')
    date = Column(Date())

    @validates('date_entered_from_schedule','date')
    def validates_date(self,key,value):
        if isinstance(value,datetime):
            value = value.date()
        return value

    date_entered_from_schedule = Column(Date())

    entities_account_id = Column(String(36), ForeignKey('account.id'))
    account = relationship('Account',foreign_keys=[entities_account_id])
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    entities_scheduled_transaction_id = Column(String(36), ForeignKey('scheduledtransaction.id'))
    entities_subcategory_id = Column(String(36), ForeignKey('subcategory.id'))
    subcategory = relationship('SubCategory')
    flag = Column(String())
    imported_date = Column(Date())
    imported_payee = Column(String())
    matched_transaction_id = Column(String(36), ForeignKey('transaction.id'))
    memo = Column(String())

    source = Column(MyEnumType(Sources))
    transfer_account_id = Column(String(36), ForeignKey('account.id'))
    transfer_subtransaction_id = Column(String(36), ForeignKey('subtransaction.id'))
    transfer_transaction_id = Column(String(36), ForeignKey('transaction.id'))
    ynab_id = Column(String())



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

    @Amounthybrid
    def cash_amount(self):
        if self.transaction and self.transaction.account and self.transaction.account.account_type != AccountTypes.CreditCard:
            return self.amount
        return 0

    @Amounthybrid
    def credit_amount(self):
        if self.transaction and self.transaction.account and self.transaction.account.account_type == AccountTypes.CreditCard:
            return self.amount
        return 0

    check_number = Column(String())
    entities_payee_id = Column(String(36), ForeignKey('payee.id'))
    entities_subcategory_id = Column(String(36), ForeignKey('subcategory.id'))
    entities_transaction_id = Column(String(36), ForeignKey('transaction.id'))
    transaction = relationship('Transaction', foreign_keys=[entities_transaction_id])

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


class SubCategory(BudgetEntity, Base):
    entities_account_id = Column(String(36), ForeignKey('account.id'))
    entities_master_category_id = Column(String(36), ForeignKey('mastercategory.id'))
    master_category = relationship('MasterCategory')
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


class MonthlySubCategoryBudgetCalculation(BudgetEntity, Base):
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


class MonthlySubCategoryBudget(BudgetEntity, Base):
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


class Account(BudgetEntity, Base):
    account_name = Column(String())
    account_type = Column(MyEnumType(AccountTypes))
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
