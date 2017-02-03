# Copyright 2014 SolidBuilds.com. All rights reserved.
#
# Authors: Ling Thio <ling.thio@gmail.com>

# DB-Adapters aims to shield basic DB operations from the underlying DB/ORM technology such as:
# - SQLAlchemy
# - MongoDB
# - More, through custom extensions
#
# DB-Adapters only aims to support very basic operations:
# - find, ifind, add, update, delete
#
# DB-Adapters is used to by Flask-User and Flask-CMS.

from __future__ import print_function
from sqlalchemy import func


class SQLAlchemyDBAdapter(object):
    def __init__(self, db):
        self.db = db


    def get_by_id(self, DataModelClass, id):
        """ Retrieve one object specified by the primary key 'pk' """
        return DataModelClass.query.get(id)


    def find(self, DataModelClass, **kwargs):
        """ Retrieve all objects matching the case sensitive filters in 'kwargs'. """
        query = self._find_with_operation(DataModelClass, '__eq__', **kwargs)
        return query.all()


    def find_first(self, DataModelClass, **kwargs):
        """ Retrieve all objects matching the case sensitive filters in 'kwargs'. """
        query = self._find_with_operation(DataModelClass, '__eq__', **kwargs)
        return query.first()


    def ifind(self, DataModelClass, **kwargs):
        """ Retrieve all objects matching the case sensitive filters in 'kwargs'. """
        query = self._find_with_operation(DataModelClass, 'ifind', **kwargs)
        return query.all()


    def ifind_first(self, DataModelClass, **kwargs):
        """ Retrieve the first object matching the case sensitive filters in 'kwargs'. """
        query = self._find_with_operation(DataModelClass, 'ifind', **kwargs)
        return query.first()


    def add(self, object):
        """ Add an object 'object'. """
        self.db.session.add(object)
        return object


    def update(self, object, **kwargs):
        """ Update object 'object' with the fields and values specified in '**kwargs'. """
        for key, value in kwargs.items():
            if hasattr(object, key):
                setattr(object, key, value)
            else:
                raise KeyError("SQLAlchemyAdapter.update(): Object '%s' has no field '%s'." % (type(object), key))


    def delete(self, object):
        """ Delete object 'object'. """
        self.db.session.delete(object)


    def commit(self):
        """ Commit all uncommitted session operations """
        self.db.session.commit()


    def get_DataModelClass_from_field_name(self, field_name):
        table_name, field_name = field_name.split('.', 1)
        for c in self.db.Model._decl_class_registry.values():
            if hasattr(c, '__table__'):
                if c.__tablename__ == table_name:
                    return c
        return None


    def _find_with_operation(self, DataModelClass, operation, **kwargs):
        """ Prepare a query using **kwargs as filters """
        # Retrieve query
        query = DataModelClass.query

        # Filter on each name/value pair in 'kwargs'
        for field_name, field_value in kwargs.items():
            # Retrieve DataModelClass.field_name
            field = getattr(DataModelClass, field_name, None)
            if field is None:
                raise KeyError("SQLAlchemyDBAdapter._find_with_operation(): Class '%s' has no field '%s'." % (
                DataModelClass, field_name))

            # Perform a case insensitive find or a case sensitive operation
            if operation == 'ifind':
                query = query.filter(func.lower(field) == func.lower(field_value))
            else:
                # Retrieve DataModelClass.field_name.operation
                field_operation = getattr(field, operation, None)
                if field_operation is None:
                    raise KeyError(
                        "SQLAlchemyDBAdapter._find_with_operation(): Field '%s.%s' has no operation '%s'." % (
                        DataModelClass, field_name, operation))
                query = query.filter(field_operation(field_value))

