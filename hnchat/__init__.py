from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from argon2 import PasswordHasher
from itsdangerous import URLSafeTimedSerializer
from flask_security import Security, SQLAlchemyUserDatastore
from flask_socketio import SocketIO


# Create app
app = Flask(__name__)
app.config.from_pyfile('config.cfg')

# Create database connection object
db = SQLAlchemy(app)

# Setup argon hash function
argon = PasswordHasher()

# Setup mail function
mail = Mail(app)

# Setup Socketio
socketio = SocketIO(app)

# Setup url timer for tokens
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Setup Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from hnchat.models import User, Role
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app)
"""
# Create a user to test with
# Only change username, email and password
@app.before_first_request
def first():
    db.create_all()
    user_datastore.create_role(name='admin')
    user_datastore.create_role(name='group')
    user_datastore.create_role(name='user')
    pw = 'P@ssw0rd20'
    pw_hash = argon.hash(pw)
    user_datastore.create_user(username='admin', email='other@cnetmail.net',
                             password=pw_hash, confirmed=True, roles=['admin'])
    db.session.commit()
"""
from hnchat import admin

from hnchat import routes