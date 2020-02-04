from hnchat import db, admin, app
from hnchat.models import User, Role, RolesUsers, HnModelView, HnAdminIndexView
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask import url_for


admin = Admin(app, index_view=HnAdminIndexView(), name='hnchat', template_mode='bootstrap3')
admin.add_view(HnModelView(User, db.session))
admin.add_view(HnModelView(Role, db.session))
admin.add_link(MenuLink(name='Return to Chat', category='', url='/chat'))