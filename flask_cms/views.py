# Copyright 2014 SolidBuilds.com. All rights reserved.
#
# Authors: Ling Thio <ling.thio@gmail.com>


from flask import abort, current_app, redirect, render_template, Blueprint
from flask import request, url_for
from flask_user import current_user, login_required, roles_required

from .cms import cms_db as db
from .models import CmsObject, CmsPage, CmsMenuItem, CmsMenuItemForm
from .forms import CmsEditPageNodeForm, CmsEditRedirectNodeForm, CmsEditPageForm

cms_blueprint = Blueprint('cms', __name__, url_prefix='/cms', template_folder='templates')

def view_page(slug, page_id):
    # Retrieve page by id
    id = CmsObject.decode_id(page_id)
    page = CmsPage.query.get_or_404(id)

    return render_template(
        'flask_cms/view_page.html',
        page=page)

@login_required
@roles_required(['Admin', 'Editor'])
def edit_page(page_id):
    # Retrieve page by id
    id = CmsObject.decode_id(page_id)
    page = CmsPage.query.get_or_404(id)

    # Create Form
    form = page.cms_manager.EditForm(formdata=request.form, obj=page)

    # Handle POST request
    if request.method=='POST' and form.validate():
        form.populate_obj(page)
        db.session.commit()
        return redirect(page.get_url())

    # Render page
    return render_template(
        'flask_cms/edit_page.html',
        form=form,
        page=page,
    )


@cms_blueprint.route('/manage_pages')
@login_required
@roles_required('Admin')
def manage_pages():
    pages = CmsObject.query.all()

    return render_template(
        'flask_cms/manage_pages.html',
        pages=pages,
    )


@cms_blueprint.route('/manage_menus')
@login_required
@roles_required('Admin')
def manage_menus():
    menus = CmsMenuItem.query.filter(CmsMenuItem.parent==None)

    return render_template(
        'flask_cms/manage_menus.html',
        menus=menus,
    )


@cms_blueprint.route('/menu_item/<menu_item_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_menu_item(menu_item_id):
    # Retrieve menu item by id
    id = CmsMenuItem.decode_id(menu_item_id)
    menu_item = CmsMenuItem.query.get_or_404(id)

    form = CmsMenuItemForm(formdata=request.form, obj=menu_item)
    form.object.query = CmsObject.query.all()

    # Handle POST request
    if request.method=='POST' and form.validate():
        form.populate_obj(menu_item)
        db.session.commit()
        return redirect(url_for('cms.manage_cms'))

    # Render page
    return render_template(
        'flask_cms/edit_menu_item.html',
        form=form,
    )

@login_required
@roles_required('cms_admin')
def cms_edit_object(id='0', type=''):
    if id != '0':
        menu_object = CmsMenuItem.query.get(id)
        if not menu_object: abort(404)
        type = menu_object.object.type

    flask_cms = current_app.flask_cms
    type_info = flask_cms.types[type]
    if not type_info: abort(404)
    return type_info.edit_view_function(id)


@login_required
@roles_required('cms_admin')
def cms_edit_page_object(id='0'):
    flask_cms = current_app.flask_cms
    db_adapter = flask_cms.db_adapter

    # Ensure that the 'Main menu' CmsMenu exists
    menu = CmsMenu.query.get(1)
    if not menu:
        menu = CmsMenu(id=1, name='Main menu')
        db_adapter.add(menu)

    # Create or Retrieve CmsPage by ID
    if id == '0':
        add_or_edit = 'Add'
        page = CmsPage()
        menu_object = CmsMenuItem(menu_id=menu.id, object=page)
    else:
        add_or_edit = 'Edit'
        menu_object = CmsMenuItem.query.get(id)
        page = menu_object.object
        if not menu_object or not page:
            abort(404)
        if page.slug == flask_cms.slugify(page.title):
            page.slug = ''
        if menu_object.label == page.title:
            menu_object.label = ''

    # Retrieve list of possible parents
    possible_parents = _get_possible_parents(menu.id, page.id)

    # Process valid POST
    form = CmsEditPageNodeForm(request.form, page)  # Initialize form
    if request.method == 'GET':
        form.menu_id.data = menu_object.menu_id
        form.parent_id.data = menu_object.parent_id
        form.order_index.data = menu_object.order_index
        form.label.data = menu_object.label

    if request.method == 'POST' and form.validate():
        form.populate_obj(page)  # Copy form fields to DB model fields
        form.populate_obj(menu_object)

        if not menu_object.parent_id:
            menu_object.parent_id = None

        if page.slug:
            page.slug = flask_cms.slugify(page.slug)
        else:
            page.slug = flask_cms.slugify(page.title)

        if not page.label:
            menu_object.label = page.title

        if id == '0':
            db_adapter.add(page)
            db_adapter.add(menu_object)

        db_adapter.commit()

        return redirect(url_for('cms.list_pages'))

    return render_template('flask_cms/edit_page_object.html',
                           add_or_edit=add_or_edit,
                           form=form,
                           menu_object=menu_object,
                           page=page,
                           possible_parents=possible_parents,
    )


@login_required
@roles_required('cms_admin')
def cms_edit_redirect_object(id):
    db_adapter = current_app.flask_cms.db_adapter

    # Ensure that the 'Main menu' CmsMenu exists
    menu = CmsMenu.query.get(1)
    if not menu:
        menu = CmsMenu(id=1, name='Main menu')
        db_adapter.add(menu)

    # Create or Retrieve CmsRedirect by ID
    if id == '0':
        add_or_edit = 'Add'
        cms_redirect = CmsRedirect()
        menu_object = CmsMenuItem(menu_id=menu.id, object=cms_redirect)
    else:
        add_or_edit = 'Edit'
        menu_object = CmsMenuItem.query.get(id)
        cms_redirect = menu_object.object
        if not menu_object or not cms_redirect:
            abort(404)

    # Retrieve list of possible parents
    possible_parents = _get_possible_parents(menu.id, cms_redirect.id)

    # Process valid POST
    form = CmsEditRedirectNodeForm(request.form, cms_redirect)  # Initialize form
    if request.method == 'GET':
        form.menu_id.data = menu_object.menu_id
        form.parent_id.data = menu_object.parent_id
        form.order_index.data = menu_object.order_index
        form.label.data = menu_object.label

    if request.method == 'POST' and form.validate():
        form.populate_obj(cms_redirect)  # Copy form fields to DB model fields
        form.populate_obj(menu_object)

        if not menu_object.parent_id:
            menu_object.parent_id = None

        if id == '0':
            db_adapter.add(cms_redirect)
            db_adapter.add(menu_object)

        db_adapter.commit()

        return redirect(url_for('cms.list_pages'))

    return render_template('flask_cms/edit_redirect_object.html',
                           add_or_edit=add_or_edit,
                           form=form,
                           menu_object=menu_object,
                           redirect=cms_redirect,
                           possible_parents=possible_parents,
    )


@login_required
@roles_required('cms_admin')
def cms_delete_object(id):
    db_adapter = current_app.flask_cms.db_adapter

    object = CmsObject.query.get(id)
    if not object:
        abort(404)

    db_adapter.delete(object)
    db_adapter.commit()

    return redirect(url_for('cms.list_pages'))


@login_required
def cms_edit_page(id):
    db_adapter = current_app.flask_cms.db_adapter

    # Retrieve page by ID
    page = CmsPage.query.get(id)
    if not page: abort(404)

    # Check for permissions
    if not page.user_can_edit(): abort(404)

    add_or_edit = 'Edit'

    # Process valid POST
    form = CmsEditPageForm(request.form, page)  # Initialize form

    if request.method == 'POST' and form.validate():
        form.populate_obj(page)  # Copy form fields to DB model fields

        db_adapter.commit()

        return redirect(url_for('cms.render_page', slug=page.slug))

    return render_template('flask_cms/edit_page.html',
                           form=form,
                           page=page,
    )


def _get_possible_parents(menu_id, current_object_id):
    def check_redirect_recursively(menu_object, current_object_id):
        """
        Return False if redirect ancestors contain current_object_id.
        Return True otherwise.
        """
        # Ancestors may not have current redirect ID
        if menu_object.object_id == current_object_id:
            return False

        # Check parent recursively
        if menu_object.parent:
            return check_redirect_recursively(menu_object.parent, current_object_id)

        # No ancestor has current redirect ID
        return True

    # Retrieve list of possible parents
    all_parents = CmsMenuItem.query.filter(CmsMenuItem.menu_id == menu_id, CmsMenuItem.object_id != current_object_id).all()
    possible_parents = []
    for parent in all_parents:
        if check_redirect_recursively(parent, current_object_id):
            possible_parents.append(parent)

    return possible_parents
