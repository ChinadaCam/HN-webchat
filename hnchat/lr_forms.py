from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from hnchat.models import User
import re

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(),
                            Length(min=3, max=16)])
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email(), Length(max=320)])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                             Length(min=8, max=24)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sing Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user: 
            raise ValidationError('Username already taken. Please choose another one.') 

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email: 
            raise ValidationError('Email already taken. Please choose another one.') 
    
    def validate_password(self, password):
        password = password.data
        if re.search('[0-9]', password) is None:
            raise ValidationError('Password must have at least a number.')
        elif re.search('[A-Z]', password) is None:
            raise ValidationError('Password must have at least a capital letter.')
        elif re.search('[a-z]', password) is None:
            raise ValidationError('Password must have at least a lowercase letter.')
        elif re.search("[!#$%&'()*+,-./:;<=>?@[\]^_`{|}~]", password) is None:
            raise ValidationError("Password must have at least a special character: [!#$%&'()*+,-./:;<=>?@[\]^_`{|}~]")

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(),
                        Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Sing In')

class AForm(FlaskForm):
    submit = SubmitField('Resend Email')

class OtpForm(FlaskForm):
    otp = StringField('OTP Code', validators=[Length(min=6, max=6)])
    submit = SubmitField('Try')