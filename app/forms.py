from app import app
from flask_wtf import FlaskForm
from flask_wtf import StringField, PasswordField, NumberField

#for logging in
Class login(FlaskForm):
    username = StringField("username")
    password

#for new account creation
Class signup():
    new_username
    new_password

#assignment creation
Class createAssignment(FlaskForm):
    number_of_qs

#assignment submission
Class submit(FlaskForm):
    student_name
    student_id
    answers = {answer1: str...}

