# Copyright 2014 SolidBuilds.com. All rights reserved.
#
# Authors: Ling Thio <ling.thio@gmail.com>

import wtforms
from wtforms import validators

from flask_user import current_user
from flask_wtf import FlaskForm

class CmsObjectManager(object):
    def get_url(self, cms_object):
        return '/' + cms_object.type + '/' + cms_object.slug + '/' + cms_object.encode_id()

    def get_edit_url(self, cms_object):
        return '/' + cms_object.type + '/' + cms_object.encode_id() + '/edit'

    def can_view(self, cms_object):
        return not cms_object.view_roles or self._has_access(cms_object.view_roles)

    def can_edit(self, cms_object):
        return not cms_object.edit_roles or self._has_access(cms_object.edit_roles)

    def _has_access(self, allowed_roles_str):
        has_access = False
        if current_user.is_authenticated:
            # Split comma separated list into a list of allowed role names
            allowed_roles = allowed_roles_str.split(',')
            # See if the user has any of the specified roles
            for role in current_user.roles:
                has_access = role.name in allowed_roles
                if has_access: break
        return has_access

class EditForm(FlaskForm):
    name = wtforms.StringField('Title', validators=[validators.DataRequired('Title is required')])
    content = wtforms.TextAreaField('Content', validators=[validators.Optional()])
    slug = wtforms.StringField('Slug', validators=[validators.Optional()])
    submit = wtforms.SubmitField('Update')


class CmsPageManager(CmsObjectManager):
    EditForm = EditForm

cms_object_manager = CmsObjectManager()
cms_page_manager = CmsPageManager()