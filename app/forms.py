from app import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField, FieldList, SelectField, SelectMultipleField
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
    number_of_questions = IntegerField("Number of Questions", validators=[DataRequired()], render_kw={"id":"num_questions"})
    questions = FieldList(QuestionForm("Question", validators=[DataRequired()]))
    submit = SubmitField("Create Assignment")
class QuestionForm(FlaskForm):
    class Meta:
        csrf = False#csrf will be handled in parent form
    question = StringField("Question Text", validators=[DataRequired()])#error class numbers based on pipeline2 string 'system_prompt_generate1'
    error_types = SelectMultipleField("Error Type", selection=[('0', 'Mental Typo'),( '1', 'Knowledge Gap'),('2', 'Misconception'),('3', 'Wrong Choice'),( '4','Structural Blindness')])


#assignment submission
class Submit(FlaskForm):
    student_name = StringField("Student Name", validators=[DataRequired()])
    student_id = StringField("Student ID", validators=[DataRequired()])
    answers = FieldList(StringField("Answer", validators=[DataRequired()]), min_entries=1)
    submit = SubmitField("Submit Assignment")

