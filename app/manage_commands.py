# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime

from app.init_app import app, db, manager
from app.models import User, Role

@manager.command
def init_db():
    """ Initialize the database."""
    # Delete all tables, then re-create all tables
    db.drop_all()
    db.create_all()
    # Add all Users
    add_users()
    add_cms_objects()


def add_users():
    """ Create users when app starts """

    # Adding roles
    editor_role = Role(name='Editor')
    admin_role = Role(name='Admin')

    # Add users
    user = add_user('Guest', 'User', 'guest@example.com', 'Password1')
    user = add_user('Editor', 'User', 'editor@example.com', 'Password1', role=editor_role)
    admin = add_user('Admin', 'User', 'admin@example.com', 'Password1', role=admin_role)

    # Save to DB
    db.session.commit()


def add_cms_objects():
    from flask_cms.models import CmsPage, CmsMenuItem

    # Add Pages
    page1 = CmsPage(name='Page One', content='Content One', slug='page-one')
    db.session.add(page1)
    page2 = CmsPage(name='Page Two', content='Content Two', slug='page-two')
    db.session.add(page2)

    # Add MenuItems
    main_menu = CmsMenuItem(name='Main Menu')
    db.session.add(main_menu)
    menu_item1 = CmsMenuItem(order=1, name=page1.name, parent=main_menu, object=page1)
    db.session.add(menu_item1)
    menu_item2 = CmsMenuItem(order=2, name=page2.name, parent=main_menu, object=page2)
    db.session.add(menu_item2)

    db.session.commit()


def add_user(first_name, last_name, email, password, role=None):
    """ Find existing user or create new user """
    user = User(email=email,
                first_name=first_name,
                last_name=last_name,
                password=app.user_manager.hash_password(password),
                active=True,
                confirmed_at=datetime.datetime.utcnow())
    if role:
        user.roles.append(role)
    db.session.add(user)
    return user

