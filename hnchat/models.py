from hnchat import db, login_manager
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
from flask import redirect, url_for, flash
from flask_security import RoleMixin, UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(120), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    attempts = db.Column(db.String(5), unique=False, default=0)
    active = db.Column(db.Boolean, nullable=False, default=False)
    roles = db.relationship('Role', secondary='roles_users',
                         backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.confirmed}', '{self.attempts}')"

    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})

class HnModelView(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')
        #return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


class HnAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        flash('You need permission, to access that page.', 'danger')
        return redirect(url_for('login'))
