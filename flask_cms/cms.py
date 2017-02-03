# Copyright 2014 SolidBuilds.com. All rights reserved.
#
# Authors: Ling Thio <ling.thio@gmail.com>

from __future__ import print_function
from sqlalchemy.inspection import inspect
from .db_adapters import SQLAlchemyDBAdapter
from .slugifier import Slugifier

cms_db = None
cms_app = None

class CmsTypeInfo(object):
    def __init__(self, type, name, edit_view_function):
        self.type = type
        self.name = name
        self.edit_view_function = edit_view_function


class CMS():
    def __init__(self, app=None, db=None, **kwargs):
        if app:
            self.init_app(app, db, **kwargs)

    def init_app(self, app, db):
        self.app = app
        app.cms = self

        global cms_app
        cms_app = app

        global cms_db
        cms_db = db
        from . import models                                # Register db.Models

        self.slugifier = Slugifier()

        from .views import cms_blueprint
        app.register_blueprint(cms_blueprint)
        self.add_url_routes(app)

        # self.db_adapter = DBAdapterClass(db)
        # self.user_id_field_name = user_id_field_name
        # self.role_id_field_name = role_id_field_name
        # self.user_id_field_name = 'member.id'
        # self.page_base_url = '/page'
        # self.admin_base_url = '/cms'
        # self.types = {}

        # from .views import cms_edit_page_object, cms_edit_redirect_object
        # self.register_type('cms_page', 'Page', cms_edit_page_object)
        # self.register_type('cms_redirect', 'Redirect', cms_edit_redirect_object)

        @app.context_processor
        def context_processor():
            return dict(flask_cms=self)

    def add_url_routes(self, app):
        from . import views

        app.add_url_rule('/page/<slug>/<page_id>', 'cms.view_page', views.view_page)
        app.add_url_rule('/page/<page_id>/edit', 'cms.edit_page', views.edit_page, methods=['GET', 'POST'])
        # app.add_url_rule(self.admin_base_url + '/list-pages', 'cms.list_pages', views.cms_list_pages)
        # app.add_url_rule(self.admin_base_url + '/add-object/<type>', 'cms.add_object', views.cms_edit_object,
        #                  methods=['GET', 'POST'])
        # app.add_url_rule(self.admin_base_url + '/object/<id>/edit', 'cms.edit_object', views.cms_edit_object,
        #                  methods=['GET', 'POST'])
        # app.add_url_rule(self.admin_base_url + '/object/<id>/delete', 'cms.delete_object', views.cms_delete_object)
        # app.add_url_rule(self.admin_base_url + '/page/<id>/edit', 'cms.edit_page', views.cms_edit_page,
        #                  methods=['GET', 'POST'])

    # def init_cms_menus(self):
    # from .models import CmsMenu
    #     menu = CmsMenu(name='Main menu')
    #     self.db_adapter.add(menu)
    #     self.db_adapter.commit()

    # def register_type(self, type, name, edit_view_function):
    #     self.types[type] = CmsTypeInfo(type, name, edit_view_function)

    def slugify(self, text):
        return self.slugifier.slugify(text)

    # def get_menu_objects(self, menu_name):
    #     from .models import CmsObject, CmsMenu, CmsMenuItem
    #
    #     menu = CmsMenu.query.filter(CmsMenu.name == menu_name).first()
    #     if menu:
    #         objects = CmsMenuItem.query \
    #             .filter(CmsMenuItem.menu_id == menu.id) \
    #             .filter(CmsMenuItem.parent_id == None) \
    #             .order_by(CmsMenuItem.order_index) \
    #             .all()
    #     else:
    #         objects = []
    #     return objects

    def get_menu(self, menu_name):
        # Find menu item by specified menu_name
        from .models import CmsMenuItem
        menu = CmsMenuItem.query.filter(CmsMenuItem.name==menu_name).first()
        return menu

    def get_first_menu_item_url(self, menu_name):
        url = '/'
        menu = self.get_menu(menu_name)
        if menu and len(menu.menu_items)>0:
            url = menu.menu_items[0].get_url()
        return url
