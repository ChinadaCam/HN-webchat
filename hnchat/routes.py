from flask import render_template, url_for, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from hnchat import app, db, argon, s, user_datastore, socketio
from hnchat.lr_forms import RegistrationForm, LoginForm, AForm, OtpForm
from hnchat.models import User
from hnchat.email import send_email
from hnchat.otp import gen_otp
from itsdangerous import SignatureExpired, BadTimeSignature
from argon2.low_level import VerifyMismatchError
from flask_socketio import emit

# Routes of the website

# Main page and Register page
@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Verify if a user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('chat'))    # Return to chat page case it's true
    form = RegistrationForm()   # Get Registration form
    # Condition for when the form is submited
    if form.validate_on_submit():
        hashed_pw = argon.hash(form.password.data)  # Hash method
        email = form.email.data
        # Set the values following the User Model in models.py
        user_datastore.create_user(username=form.username.data, email=email,
                             password=hashed_pw, roles=['user'])
        db.session.commit()
        # Email Structure -> that follows email.py function args
        token = s.dumps(email, salt='hn_mail-check')    # Encrypt data to pass on url_for
        link = url_for('mail_check', token=token, _external=True)   # Link encrypted that will be sent
        ## HTML for the email structue
        html = render_template('user/activate.html', confirm_url=link, username=form.username.data)
        subject = 'Please confirm yout account - Hey Neighbor'  # Mail Subject
        send_email(email, subject, html)    # Funtion to send the email
        mail = s.dumps(email, salt='hn_mail_check')    # Encrypt data to pass on url_for
        session['mail_token_link'] = link
        session['mail_token_user'] = form.username.data
        return redirect(url_for('conf_mail', token_mail=mail))    # Redirect to the confirmation page
    # Else return the register page
    return render_template('register.html', title='Register', form=form)

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verify if a user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    form = LoginForm()  # Get Login form
    # Condition for when the form is submited
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()    # Check if email exists
        confirmed = User.query.filter_by(email=email, confirmed=True).first()   # Check if user verified the account
        blocked = User.query.filter_by(email=email, attempts=3).first()
        # Check if user and password check
        try:
            if user and argon.verify(user.password, form.password.data):
                # Condition to user account verified
                if confirmed:
                    if blocked:
                        flash('Your account was blocked. Please contact an admin: heyneighbor.atec@gmail.com', 'danger')
                    else:
                        user.attempts = 0
                        db.session.commit()
                        session['otp_code'] = gen_otp()
                        session['otp_mail'] = email
                        otp_code = session.get('otp_code')
                        html = render_template('user/otpmail.html', otp_code=otp_code)
                        subject = 'Two-Factor Authentication - Hey Neighbor'  # Mail Subject
                        send_email(email, subject, html)    # Funtion to send the email
                        return redirect(url_for('otp_page'))
                else:
                    mail = s.dumps(email, salt='hn_mail_check')    # Encrypt the url_for arg informatin
                    return redirect(url_for('conf_mail', token_mail=mail))    # Return to verify account page case it's not verified
            else:   
                if blocked:
                    flash('Your account was blocked. Please contact an admin: heyneighbor.atec@gmail.com', 'danger')
                else:
                    if user:
                        user.attempts = User.attempts + 1
                        db.session.commit()
                    flash('Login Unsuccessful. Please check email and password.', 'danger')
        # From argon2.lowlevel.py import exception VerifyMismatchError and change condition
        except VerifyMismatchError:
            if blocked:
                flash('Your account was blocked. Please contact an admin: heyneighbor.atec@gmail.com', 'danger')
            else:
                if user:
                    user.attempts = User.attempts + 1
                    db.session.commit()
                flash('Login Unsuccessful. Please check email and password.', 'danger')
    # Else return the Login page
    return render_template('login.html', title='Login', form=form)

# Logout user
@app.route('/logout')
@login_required
def logout():
    logout_user()   # Function to logout the user
    return redirect(url_for('login'))

# Chat Page
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    return render_template('chat.html', username=current_user.username)

def messageRecived():
  print( 'message was received!!!' )

@app.route('/otp', methods=['GET', 'POST'])
def otp_page():
    form = OtpForm()
    if form.validate_on_submit():
        if session.get('otp_code') == form.otp.data:
            email = session.get('otp_mail')
            user = User.query.filter_by(email=email).first()
            login_user(user)
            if current_user.has_role('admin'):
                return redirect(url_for('admin_dash'))
            else:
                return redirect(url_for('chat'))
        else:
            flash('Codigo errado', 'danger')
    return render_template('otp.html', otp=session.get('otp_code'), form=form)

# Admin Page
@app.route('/admin')
@login_required
# @roles_required('admin')
def admin_dash():
    return self

# Verify Account Page
@app.route('/mail_conf/<token_mail>', methods=['GET', 'POST'])
def conf_mail(token_mail):
    try:
        email = s.loads(token_mail, salt='hn_mail_check', max_age=3600)    # Decrypt the url_for arg informatin
        form = AForm()
        if form.validate_on_submit():
            link = session.get('mail_token_link')   # Session Link
            username = session.get('mail_token_user')   # Session Username
            # Resend Email
            html = render_template('user/activate.html', confirm_url=link, username=username)
            subject = 'Please confirm yout account - Hey Neighbor' 
            send_email(email, subject, html)   
            mail = s.dumps(email, salt='hn_mail_check')
            return redirect(url_for('conf_mail', token_mail=mail))
        return render_template('activate.html', email=email, form=form)
    except SignatureExpired:
        # Token Expired
        email = s.loads(token, salt='hn_mail_check')
        confirmed = User.query.filter_by(email=email, confirmed=True).first()
        if not confirmed:
            User.query.filter_by(email='hnchat@jancloud.net').delete()
            db.session.commit()
        else:
            flash('Your account is already activated.', 'warning')
            return redirect(url_for('login'))
        return render_template('activate.html', expired=True)
    except BadTimeSignature:
        # Token Invalid Format
        return '<h1>Invalid token!</h1>'

# Verify Account Function Page
@app.route('/mail_check/<token>')
def mail_check(token):
    try:
        email = s.loads(token, salt='hn_mail-check', max_age=3600)    # 3600 Decrypt the url_for arg informatin
    except SignatureExpired:
        # Token Expired
        email = s.loads(token, salt='hn_mail-check')
        confirmed = User.query.filter_by(email=email, confirmed=True).first()
        if not confirmed:
            User.query.filter_by(email='hnchat@jancloud.net').delete()
            db.session.commit()
        else:
            flash('Your account is already activated.', 'warning')
            return redirect(url_for('login'))
        return render_template('activate.html', expired=True)
    except BadTimeSignature:
        # Token Invalid Format
        return '<h1>Invalid token!</h1>'
    # If user account already activated, user can't use the token
    confirmed = User.query.filter_by(email=email, confirmed=True).first()
    if confirmed:
        flash('Your account is already activated. Please Log In.', 'warning')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()    # Get user
    # Case user doesn't exist anymore, like it's deleted before activate account.
    if user:
        user.confirmed = True   # Change the confirmed value to True
        db.session.commit()    # Commit the database changes
        login_user(user)
        # Return the Activate Page
        return render_template('activate.html', token=True)
    else:
        flash("Your account doens't exist anymore. Please create another.", 'warning')
        return redirect(url_for('register'))

# Flask Socket IO
@socketio.on( 'my event' )
def handle_my_custom_event( json ):
  print( 'recived my event: ' + str( json ) )
  socketio.emit( 'my response', json, callback=messageRecived )

#Room

@app.route('/room',methods=['GET','POST'])
def room():
    username = current_user.username
    room = request.args.get('room')
    
 
    if username and room:
        return render_template('room.html',username=username,room=room)
    else:
        return redirect(url_for('chat'))
 

#Error 404
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error404.html') 

