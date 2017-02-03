Flask-CMS
=========

A minimalist Content Management System (CMS) using the Flask application framework.

Requirements
------------

The Role model must have a `name` field, and a `Admin` role and a `Editor` role must exist.

The User model must have a `roles` field that contains a list of Roles.

A User must have an `Admin` role to manage CMS Menu Items.

A User must have an `Editor` role to manage and edit CMS Pages.

Install
-------

For now, retrieve from: https://github.com/lingthio/Flask-CMS-demo

Setup
-----
::

    from flask import Flask
    from flask_cms import CMS

    app = Flask(__name__)           # The WSGI compliant web application object
    db = SQLAlchemy()               # Setup Flask-SQLAlchemy

    def init_app():
        # Setup Flask-SQLAlchemy
        db.init_app(app)

        # Setup Flask-CMS
        cms = CMS(app, db)

Add an `Admin` Role and a `Editor` Role to the Database

Add an `admin@example.com` user that has an `Admin` Role.

Add an `editor@example.com` user that has an `Editor` Role.

Manage Pages
------------

Login as `admin@example.com`

Point your browser to http://localhost:5000/cms/manage_pages

Point your browser to http://localhost:5000/cms/manage_menus


