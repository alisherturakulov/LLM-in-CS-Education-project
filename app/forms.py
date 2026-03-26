from app import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField
from wtforms.validators import DataRequired

#for logging in
class Login(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    remember_me = BooleanField("remember_me", validators=[DataRequired()])


#for new account creation
class Signup():
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField("passowrd", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

#assignment creation
class CreateAssignment(FlaskForm):
    number_of_qs = IntegerField("questionCount", validators=[DataRequired()])
    submit = SubmitField("Create Assignment")

#assignment submission
class Submit(FlaskForm):
    student_name = SringField("studentName", validators=[DataRequired()])
    student_id = StringField("studentID", validators=[DataRequired()])
    answers = FieldList(StringField("answer"), min_entries=1)
    submit = SubmitField("Submit Assignment")

