from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.sqltypes import String, Boolean, Integer


class Converter(object):
    @classmethod
    def amount_in(cls, value):
        return int(1000 * value)

    @classmethod
    def amount_out(cls, value):
        return float(value / 1000)

    @classmethod
    def jsondata_in(cls, value):
        return int(1000 * value)

    @classmethod
    def jsondata_out(cls, value):
        return float(value / 10000)

    @classmethod
    def date_in(cls, value):
        return value.strftime('%Y-%m-%d')

    @classmethod
    def date_out(cls, value):
        return datetime.strptime(value, '%Y-%m-%d').date()


class Amount(Integer):
    pass


class Dates(String):
    pass


class IgnorableString(String):
    pass


class IgnorableBoolean(Boolean):
    pass

class Amounthybrid(hybrid_property):
    pass
