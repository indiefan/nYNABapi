from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from Entity import Entity, Base, RootEntity
from types import ArrayType


class CatalogEntity(Entity):
    @declared_attr
    def parent_id(self):
        return Column(ForeignKey('catalog.id'))

    @declared_attr
    def parent(self):
        return relationship('Catalog')


class Catalog(Base, RootEntity):
    ce_user_budgets = relationship('UserBudget')
    ce_user_settings = relationship('UserSetting')
    ce_budget_versions = relationship('BudgetVersion')
    ce_users = relationship('User')
    ce_budgets = relationship('CatalogBudget')


class CatalogBudget(Base, CatalogEntity):
    budget_name = Column(String)


class User(Base, CatalogEntity):
    username = Column(String)
    trial_expires_on = Column(String)
    email = Column(String)
    feature_flags = Column(ArrayType)
    is_subscribed = Column(Boolean)


class UserSetting(Base, CatalogEntity):
    setting_name = Column(String)
    user_id = Column(ForeignKey('user.id'))
    user = relationship('User', foreign_keys=user_id, backref='settings')
    setting_value = Column(String)


class UserBudget(Base, CatalogEntity):
    budget_id = Column(ForeignKey('catalogbudget.id'))
    budget = relationship('CatalogBudget')

    user_id = Column(ForeignKey('user.id'))
    user = relationship('User', foreign_keys=user_id, backref='budgets')
    permissions = Column(String)


class BudgetVersion(Base, CatalogEntity):
    date_format = Column(String)
    last_accessed_on = Column(String)
    currency_format = Column(String)
    budget_id = Column(ForeignKey('catalogbudget.id'))
    budget = relationship('CatalogBudget', foreign_keys=budget_id)
    version_name = Column(String)
    source = Column(String)
