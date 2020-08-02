# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
import datetime
import os
import uuid

from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import LoginManager, current_user, login_required
from flask_mail import Mail, Message

from auth import auth as auth_blueprint
from db_operations import (create_listing, create_listing_without_id,
                           delete_user, get_listing, get_listings, get_user)
from forms import AdoptionForm, CreateListingForm, LoginForm, SignupForm
from gcloudstorage import upload_blob

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'petadoption.sps@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD") # SET password as environment variable

app.register_blueprint(auth_blueprint)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

mail = Mail(app)

def send_email(poster_email, adopter_email, adopter_name, email_message):
    msg = Message('Someone wants to adopt your pet!', sender='petadoption.sps@gmail.com',
                recipients=[poster_email], reply_to=adopter_email)
    msg.body = f'''Hello!

    {adopter_name} is interested in your pet! They said:
    {email_message}
    If you think they will make a good family for your pet, simply reply to this message to send them an email.
    
    Cheers!
    '''

    mail.send(msg)

@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        listings = get_listings()
        form = CreateListingForm()
        adoptform = AdoptionForm()
        loginform = LoginForm()
        signupform = SignupForm()
        return render_template('main.html', listings=listings, form=form, adoptform=adoptform, loginform=loginform, signupform=signupform)
    elif request.method == 'POST':
        for key, upload in request.files.items():
            identity = str(uuid.uuid4())  # or uuid.uuid4().hex
            try:
                img_url = upload_blob(request.files[key], identity, content_type=upload.content_type)
                app.logger.info(f'uploaded images to gcloud with url {img_url}')
            except Exception as e:
                app.logger.error(e)
        form_dict = request.form.to_dict()
        try:
            new_listing = create_listing_without_id(
                form_dict['pet_name'],
                form_dict['animal'],
                form_dict['breed'],
                form_dict['dob'],
                form_dict['description_of_pet'],
                img_url,
                form_dict['email'],
            )
            create_listing(new_listing)
        except Exception as e:
            app.logger.error(e)
        return redirect(url_for('root'))

@app.route('/adopt/<listing_id>', methods=['POST'])
def adopt(listing_id):
    listing = get_listing(listing_id)
    if not listing:
        app.logger.error(f"Failed to get listing: {listing_id}")
        abort(404, description=f"Failed to get listing: {listing_id}")
        return
    
    adopter_name = request.form["name"]
    adopter_email = request.form["email"]
    email_message = request.form["message"]

    poster_email = listing.user_email

    send_email(poster_email, adopter_email, adopter_name, email_message)
    app.logger.info(f"Sent email to {poster_email} with message from {adopter_email}")

    return redirect(url_for('root'))

@app.route('/users/<email>', methods=['GET', 'DELETE'])
def handle_user(email):
    if request.method == 'GET':
        user = get_user(email)
        if not user:
            app.logger.error(f"Failed to get user: {email}")
            abort(404, description=f"Failed to get user: {email}")
        return user.to_json()
    if request.method == 'DELETE':
        deleted = delete_user(email)
        if not deleted:
            app.logger.error(f"Failed to delete user: {email}")
            abort(500, f"Failed to delete user: {email}")
        return ('', 204)

@app.route('/listings', methods=['GET'])
def handle_listings():
    if request.method == 'GET':
        listings = get_listings()
        if not listings:
            app.logger.error("Failed to get listings")
            abort(500, "Failed to get listings")
        return jsonify(listings)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@login_manager.user_loader
def load_user(user_id):
    ''' 
    Take unicode id of user and return corresponding user object
    See https://flask-login.readthedocs.io/en/latest/#how-it-works

    We use email as the user_id
    '''
    return get_user(user_id)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [START gae_python38_render_template]
