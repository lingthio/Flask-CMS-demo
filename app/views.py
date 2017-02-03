# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import current_app, redirect, render_template, render_template_string, Blueprint
from flask import request, url_for
from flask_user import current_user, login_required, roles_accepted

from app.init_app import app, db
from app.models import UserProfileForm

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    return redirect(current_app.cms.get_first_menu_item_url('Main Menu'))


