import logging

from flask import (Flask, Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from db_operations import create_user, get_user, update_user
from forms import LoginForm, SignupForm, RequestVerificationEmail
from users import User

auth = Blueprint('auth', __name__)

def send_verification_email(user):
    auth_app = Flask(__name__)
    auth_app.config['SECRET_KEY'] = current_app.config['SECRET_KEY']
    auth_app.config['MAIL_SERVER'] = current_app.config['MAIL_SERVER']
    auth_app.config['MAIL_PORT'] = current_app.config['MAIL_PORT']
    auth_app.config['MAIL_USE_TLS'] = current_app.config['MAIL_USE_TLS']
    auth_app.config['MAIL_USERNAME'] = current_app.config['MAIL_USERNAME']
    auth_app.config['MAIL_PASSWORD'] = current_app.config['MAIL_PASSWORD']
    mail = Mail(auth_app)
    
    if not user.verified:
        token = user.get_token(86400)
        msg = Message('Pet Adoption: Email Verification', sender='petadoption.sps@gmail.com',
                    recipients=[user.email])
        msg.body = f'''Welcome to PetAdoption! Please click this link to verify your account:
    {url_for('auth.verify_account', token=token, _external=True)}
    The link above will expire in 24 hours. If you missed this email, please click the link below to request a new valid link:
    {url_for('auth.request_verification_email', _external=True)}
    '''
        mail.send(msg)

@auth.route('/verify-account/<token>', methods = ['GET'])
def verify_account(token):
    email = User.verify_token(token)
    user = get_user(email)
    if user is None:
        flash('Your link has expired or is invalid! Request a new valid link!')
        return redirect(url_for('auth.request_verification_email'))
    user.verified = True
    update_user(user.email, user.to_firestore())
    flash('Account verified! You can now log in')
    return redirect(url_for('auth.login'))

@auth.route('/request_verification_email', methods = ['GET', 'POST'])
def request_verification_email():
    form = RequestVerificationEmail(request.form)
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user:
            send_verification_email(user)
        flash('Link has been sent to your email. It will expire in 24 hours.')
        return redirect(url_for('auth.login'))
    return render_template('verify.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    log = current_app.logger

    if current_user.is_authenticated:
        return redirect(url_for('root'))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        log.info('valid form')
        email = form.email.data
        password = form.password.data

        user = get_user(email)
        if not user or not check_password_hash(user.password, password):
            log.info('login failed - wrong login details')
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        
        if not user.verified:
            log.info('login failed - user not verified')
            flash('Please check your email and verify your account first!')
            return redirect(url_for('auth.login'))

        log.info('login success')
        login_user(user, remember=True)
        if current_user.is_authenticated:
            return redirect(url_for('root'))

    return render_template('login.html', loginform=form)

@auth.route('/signup', methods=['GET','POST'])
def signup():
    log = current_app.logger

    if current_user.is_authenticated:
        return redirect(url_for('root'))
    
    form = SignupForm(request.form)
    if form.validate_on_submit():
        # add user to database
        log.info('valid signup form')
        email = form.email.data
        name = form.name.data
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        
        new_user = User(email, name, hashed_password, None, False, None)
        create_user(new_user)
        send_verification_email(new_user)
        
        flash('User created! Please check your email to verify your account!')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)

@auth.route('/logout')
def logout():
    if current_user:
        logout_user()
    return redirect(url_for('root'))
