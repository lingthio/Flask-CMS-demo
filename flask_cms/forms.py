# Copyright 2014 SolidBuilds.com. All rights reserved.
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask import current_app
from flask_wtf import Form
from wtforms import HiddenField, IntegerField, SelectField, StringField, SubmitField, validators
from wtforms.ext.sqlalchemy.orm import QuerySelectField


class CmsEditPageNodeForm(Form):
    """ This form is used by the CMS admin to edit the Page Node (not the Page)
    """
    def role_query_factory():
        cms = current_app.flask_cms
        RoleClass = cms.db_adapter.get_DataModelClass_from_field_name(cms.role_id_field_name)
        return RoleClass.query

    # CmsPage fields
    title = StringField('Title', validators=[validators.DataRequired('Title is required')])
    content = StringField('Content')
    slug = StringField('URL name')
    view_role = QuerySelectField('Role required for viewing', query_factory=role_query_factory,
            get_label='name', allow_blank=True)
    edit_role = QuerySelectField('Role required for editing', query_factory=role_query_factory,
            get_label='name', allow_blank=True)

    # CmsMenuItem fields
    menu_id = HiddenField('Menu')
    parent_id = IntegerField('Parent menu')
    order_index = IntegerField('Menu order')
    label = StringField('Menu label')

    submit = SubmitField('Save')


class CmsEditRedirectNodeForm(Form):
    # CmsPage fields
    label = StringField('Menu label', validators=[validators.DataRequired()])
    redirect_url = StringField('Redirect URL', validators=[validators.DataRequired()])

    # CmsMenuItem fields
    menu_id = HiddenField('Menu')
    parent_id = IntegerField('Parent menu')
    order_index = IntegerField('Menu order')

    submit = SubmitField('Save')


class CmsEditPageForm(Form):
    """ This form is used by the CMS editor to edit the Page (not the Page Node)
    """

    # CmsPage fields
    title = StringField('Title', validators=[validators.DataRequired('Title is required')])
    content = StringField('Content')

    submit = SubmitField('Save')
