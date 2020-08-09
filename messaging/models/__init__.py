from datetime import date
from sqlalchemy import inspect

from messaging.messaging_system import db


class DatabaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        data = {}
        for column in inspect(self).mapper.column_attrs:
            column_data = getattr(self, column.key)
            if isinstance(column_data, date):
                data[column.key] = str(column_data)
            else:
                data[column.key] = column_data
        return data
