from app import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField, FieldList, SelectField, SelectMultipleField, FormField
from wtforms.validators import DataRequired

#for logging in
class Login(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign in")


#for new account creation
class Signup(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

#assignment creation
class QuestionForm(FlaskForm):
    class Meta:
        csrf = False#csrf will be handled in parent form
    question = StringField("Question Text", validators=[DataRequired()])#error class numbers based on pipeline2 string 'system_prompt_generate1'
    error_types = SelectMultipleField("Error Type", validators=[DataRequired()], choices=[('0', 'Mental Typo'),( '1', 'Knowledge Gap'),('2', 'Misconception'),('3', 'Wrong Choice'),( '4','Structural Blindness')])
    answer_type = SelectField("Answer Input Type", validators=[DataRequired()], choices=[('0','Text'),('1', 'Highlight')])
class CreateAssignment(FlaskForm):
    number_of_questions = IntegerField("Number of Questions", validators=[DataRequired()])
    questions = FieldList( FormField(QuestionForm), min_entries=1)
    submit = SubmitField("Create Assignment")



#assignment submission
class Submit(FlaskForm):
    student_name = StringField("Student Name", validators=[DataRequired()])
    student_id = StringField("Student ID", validators=[DataRequired()])
    answers = FieldList(StringField("Answer", validators=[DataRequired()]), min_entries=0)
    answer_logs = FieldList(StringField("History", render_kw={"hidden":True}), min_entries=0)
    submit = SubmitField("Submit Assignment")

