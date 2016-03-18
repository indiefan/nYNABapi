from sqlalchemy import Column
from sqlalchemy.types import String
from sqlalchemy.schema import ForeignKey

from pynYNAB.db.Entity import Entity


class CatalogBudget(Entity):
    budget_name = Column(String())


class UserBudget(Entity):
    budget_id = Column(String(36), ForeignKey('CatalogBudget'))
    user_id = Column(String())
    permissions = Column(String())


class UserSetting(Entity):
    setting_name=Column(String())
    user_id = Column(String(36),ForeignKey('User'))
    setting_value = Column(String())


class User(Entity):
    username = Column(String())
    trial_expires_on = Column(String())
    email = Column(String())


class BudgetVersion(Entity):
    date_format = Column(String())
    last_accessed_on = Column(String())
    currency_format = Column(String())
    budget_id = Column(String(36),ForeignKey('CatalogBudget'))
    version_name = Column(String())
