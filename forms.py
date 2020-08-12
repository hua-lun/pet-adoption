from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (DateField, PasswordField, SelectField, StringField,
                     SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Email, Length, Optional,
                                ValidationError)

from db_operations import get_user


class AdoptionForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    message = TextAreaField(validators=[DataRequired(), Length(max=400)])
    submit = SubmitField('Submit')


class CreateListingForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    pet_name = StringField(validators=[DataRequired()])
    animal = SelectField("dog", choices=[("dog", "dog"), ("cat", "cat"), ("others", "other animals")])
    breed = StringField(validators=[DataRequired()])
    dob = DateField('Pick a Date', format="%m/%d/%Y")
    description_of_pet = TextAreaField(validators=[Optional(), Length(max=200)])
    upload_img = FileField('image', validators=[
        FileRequired(),
        FileAllowed(tuple('jpg jpe jpeg png gif svg bmp webp'.split()), 'Images only!')
    ])
    submit = SubmitField('Submit')


class EditListingForm(FlaskForm):
    pet_name = StringField(validators=[DataRequired()])
    animal = SelectField("dog", choices=[("dog", "dog"), ("cat", "cat"), ("others", "other animals")])
    breed = StringField(validators=[DataRequired()])
    dob = DateField('Pick a Date', format="%m/%d/%Y")
    description_of_pet = TextAreaField(validators=[Optional(), Length(max=200)])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(form, email_field):
        user = get_user(email_field.data)
        if user:
            raise ValidationError(f'Email {email_field.data} has already been taken, please use another email')

class RequestVerificationEmail(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    send = SubmitField('Resend Email')