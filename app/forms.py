from app import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField, FieldList
from wtforms.validators import DataRequired

#for logging in
class Login(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me", validators=[DataRequired()])
    submit = SubmitField("Sign in")


#for new account creation
class Signup(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

#assignment creation
class CreateAssignment(FlaskForm):
    number_of_questions = IntegerField("Number of Questions", validators=[DataRequired()])
    submit = SubmitField("Create Assignment")

#assignment submission
class Submit(FlaskForm):
    student_name = StringField("Student Name", validators=[DataRequired()])
    student_id = StringField("Student ID", validators=[DataRequired()])
    answers = FieldList(StringField("Answer", validators=[DataRequired()]), min_entries=1)
    submit = SubmitField("Submit Assignment")

