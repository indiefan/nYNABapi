from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import String
from sqlalchemy import Column as OriginalColumn

from pynYNAB.db import Base
from pynYNAB.db.Entity import Entity, Column, Boolean
from pynYNAB.roots import Root, ListOfEntities


class Catalog(Root, Base):
    OPNAME = 'syncCatalogData'

    ce_user_budgets = ListOfEntities('UserBudget')
    ce_user_settings = ListOfEntities('UserSetting')
    ce_budget_versions = ListOfEntities('BudgetVersion')
    ce_users = ListOfEntities('User')
    ce_budgets = ListOfEntities('CatalogBudget')


class CatalogEntity(Entity):
    @declared_attr
    def catalog_id(self):
        return OriginalColumn(String(36), ForeignKey('catalog.id'))

    @declared_attr
    def parent(self):
        return relationship("Catalog")


class CatalogBudget(CatalogEntity, Base):
    budget_name = Column(String())


class UserBudget(CatalogEntity, Base):
    budget_id = Column(String(36), ForeignKey('catalogbudget.id'))
    user_id = Column(String())
    permissions = Column(String())


class UserSetting(CatalogEntity, Base):
    setting_name = Column(String())
    user_id = Column(String(36), ForeignKey('user.id'))
    setting_value = Column(String())


class User(CatalogEntity, Base):
    username = Column(String())
    trial_expires_on = Column(String())
    email = Column(String())
    feature_flags = Column(String())
    is_subscribed = Column(Boolean())


class BudgetVersion(CatalogEntity, Base):
    date_format = Column(String())
    last_accessed_on = Column(String())
    currency_format = Column(String())
    budget_id = Column(String(36), ForeignKey('catalogbudget.id'))
    version_name = Column(String())
