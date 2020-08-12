import logging
import os

from firebase_admin import credentials, firestore, initialize_app
from flask import current_app

from listings import Listing
from users import User

# Initialize Firestore DB
cred = credentials.Certificate('servicekey.json')
default_app = initialize_app(cred)
db = firestore.client()
users_db = db.collection('users')
listings_db = db.collection('listings')

# Database structure
#
# db.collection('users')
#   email [String]
# 	profile - JSON object
#       name [String]
#       contact_number [String]
# 	listings - list of listing_id

#
# db.collection('listings')
#   listing_id [String]
#   name [String]
#   animal [String]
#   breed [String]
#   DOB [Unix timestamp - int]
#   img_url [String]
#   description_of_pet [String]
#   user_email [String]


def create_user(user: User):
    log = current_app.logger
    log.info('creating new user %s', user.email)
    try:
        res = users_db.document(user.email).set(user.to_firestore())
        log.info('created new user %s at %s', user.email, res.update_time)
        return True
    except Exception as e:
        log.error(e)
        return False


def get_user(email):
    log = current_app.logger
    try:
        user = users_db.document(email).get()
        if user.exists:
            return User.from_firestore(email, user.to_dict())
        return None
    except Exception as e:
        log.error(e)
        return None


def update_user(user_email, user_details):
    log = current_app.logger
    try:
        users_db.document(user_email).update(user_details)
        return True
    except Exception as e:
        log.error(e)


def delete_user(user_email):
    log = current_app.logger
    try:
        users_db.document(user_email).delete()
        return True
    except Exception as e:
        log.error(e)
        return False


def create_listing(listing):
    log = current_app.logger
    try:
        res = listings_db.document(listing.listing_id).set(listing.to_firestore())
        log.info(res.update_time)
        return True
    except Exception as e:
        log.error(e)
        return False

def delete_listing(listing):
    log = current_app.logger
    try:
        listings_db.document(listing).delete()
        return True
    except Exception as e:
        log.error(e)
        return False

def create_empty_listing():
    log = current_app.logger
    try:
        doc_ref = listings_db.document()
        return doc_ref.id
    except Exception as e:
        log.error(e)
        return None

def create_listing_without_id(pet_name, animal, breed, dob, description, img_url, user_email):
    listing_id = create_empty_listing()
    return Listing(pet_name, animal, breed, dob, description, img_url, user_email, listing_id)


def get_listing(listing_id):
    log = current_app.logger
    try:
        listing = listings_db.document(listing_id).get()

        if listing.exists:
            listing = listing.to_dict()
            if not listing.get('description'):
                listing['description'] = ''
            return Listing.from_firestore(listing_id, listing)
        return None
    except Exception as e:
        log.error(e)
        return None

def get_listings():
    listings = listings_db.stream()

    return [{"listing_id": l.id,  **l.to_dict()} for l in listings]


def update_listing(listing_id, listing_details):
    log = current_app.logger
    try:
        listings_db.document(listing_id).update(listing_details)
        return True
    except Exception as e:
        log.error(e)

