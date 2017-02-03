# Copyright 2014 SolidBuilds.com. All rights reserved.
#
# Authors: Ling Thio <ling.thio@gmail.com>

# Flask-CMS provides a standard Object hierarchy out-of-the box, and allows developers
# To add or customize Objects by deriving custom Object classes from existing Object classes.

# Standard Object Hierarchy:
# - CmsObject
#   - CmsPage
#   - CmsBlog

# Menu Objects
# - CmsMenu
#   - CmsMenuItem

from hashids import Hashids
from sqlalchemy.orm import mapper, backref
from sqlalchemy.sql import func, text
import wtforms
from wtforms import validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from flask import url_for, current_app
from flask_user import current_user
from flask_wtf import FlaskForm

from .cms import cms_db as db, cms_app as app
from .managers import cms_object_manager, cms_page_manager


# This Mixin adds encode_id() and decode_id() to any SQLAlchemy Model class.
# These methods are used obfuscate Database IDs
class EncodeIdMixin(object):
    def encode_id(self):
        encoded_id = self.__class__.hashids.encode(self.id)     # Encode a list of integers: [self.id,]
        return encoded_id

    @classmethod
    def decode_id(cls, encoded_id):
        ids = cls.hashids.decode(encoded_id)                    # ids is a list of integers: [id,]
        return ids[0] if ids else 0


class CmsObject(db.Model, EncodeIdMixin):
    """
    Base model for all CMS data models
    """
    __tablename__ = 'cms_objects'
    cms_manager = cms_object_manager
    hashids = Hashids(salt='CmsObject'+app.config.get('SECRET_KEY', None), min_length=10)

    id = db.Column(db.Integer(), primary_key=True)

    # Polymorphic information
    type = db.Column(db.String(50), nullable=False, server_default='')
    __mapper_args__ = {
        'polymorphic_identity': 'base',
        'polymorphic_on': type
    }

    view_roles = db.Column(db.String(200), nullable=False, server_default='')
    edit_roles = db.Column(db.String(200), nullable=False, server_default='Editor,Admin')

    # owner_id = db.Column(db.Integer, db.ForeignKey(global_cms.user_id_field_name, ondelete="SET NULL"), nullable=True)
    # owner = db.relationship(global_cms.db_adapter.get_DataModelClass_from_field_name(global_cms.user_id_field_name))
    #
    # view_role_id = db.Column(db.Integer, db.ForeignKey(global_cms.role_id_field_name, ondelete="SET NULL"), nullable=True)
    # view_role = db.relationship(global_cms.db_adapter.get_DataModelClass_from_field_name(global_cms.role_id_field_name),
    #         foreign_keys=[view_role_id])
    #
    # edit_role_id = db.Column(db.Integer, db.ForeignKey(global_cms.role_id_field_name, ondelete="SET NULL"), nullable=True)
    # edit_role = db.relationship(global_cms.db_adapter.get_DataModelClass_from_field_name(global_cms.role_id_field_name),
    #         foreign_keys=[edit_role_id])

    name = db.Column(db.String(200), nullable=False, server_default='')
    content = db.Column(db.Text(), nullable=False, default='')
    slug = db.Column(db.String(200), nullable=False, server_default='')

    published_on = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    modified_at = db.Column(db.TIMESTAMP, nullable=False, default=func.now(), onupdate=func.now())

    def get_url(self):
        return self.cms_manager.get_url(self)

    def get_edit_url(self):
        return self.cms_manager.get_edit_url(self)

    def can_edit(self):
        return self.cms_manager.can_edit(self)


class CmsPage(CmsObject):
    __tablename__ = 'cms_pages'
    cms_manager = cms_page_manager

    id = db.Column(db.Integer(), db.ForeignKey('cms_objects.id'), primary_key=True)

    # Polymorphic information
    __mapper_args__ = {
        'polymorphic_identity': 'page',
    }

    def get_url(self):
        return self.__class__.cms_manager.get_url(self)


# class CmsBlogEntry(CmsObject):
#     id = db.Column(db.Integer(), db.ForeignKey('cms_objects.id'), primary_key=True)
#     __tablename__ = 'cms_blog_entries'
#
#     # Polymorphic information
#     __mapper_args__ = {
#         'polymorphic_identity': 'blog',
#     }
#     base_url = '/blog'


class CmsMenuItem(db.Model, EncodeIdMixin):
    """
    """
    __tablename__ = 'cms_menu_items'
    hashids = Hashids(salt='CmsMenuItem'+app.config.get('SECRET_KEY', None), min_length=10)


    id = db.Column(db.Integer(), primary_key=True)
    object_id = db.Column(db.Integer(), db.ForeignKey('cms_objects.id'), nullable=True)
    parent_id = db.Column(db.Integer(), db.ForeignKey('cms_menu_items.id'), nullable=True)

    order = db.Column(db.Integer(), nullable=False, server_default='0')
    name = db.Column(db.String(100), nullable=False, server_default='')

    # Relationships
    object = db.relationship('CmsObject', uselist=False)
    parent = db.relationship(
        'CmsMenuItem',
        remote_side=[id],
        backref=backref('menu_items', order_by='CmsMenuItem.order'),
    )

    def get_url(self):
        return self.object.get_url()

class CmsMenuItemForm(FlaskForm):
    name = wtforms.StringField('Name', validators=[validators.DataRequired('Name is required')])
    object = QuerySelectField('Page', get_label='name')
    submit = wtforms.SubmitField('Update')
