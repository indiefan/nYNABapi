import uuid

from sqlalchemy import TypeDecorator, types
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.dialects.postgresql import UUID

from pynYNAB.schema.enums import AccountTypes


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

class Amount(TypeDecorator):
    """Amount in nYNAB"""

    impl = types.Integer

    def process_bind_param(self, value, dialect):
        return int(1000*value)

    def process_result_value(self, value, dialect):
        return float(value/1000)

import json
class Dates(TypeDecorator):
    """Amount in nYNAB"""

    impl = types.String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)