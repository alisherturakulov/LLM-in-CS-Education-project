#routing for flask project
from app import app
from flask import render_template, request, jsonify
from pipeline import check_answer, pipeline2
from app.forms import Login, Signup, CreateAssignment, Submit
#import db from module where initialized 



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
    #check db for authentication
    
    logged_in = Login.validate_on_submit()
    
    if (logged_in):
        return render_template('form-creator.html')#uses jinja template engine
    else:
        return render_template('login.html', login_form=Login, signup_form=Signup)


@app.route('/create-assignment', methods=['GET'])
def create_questions():
    data = request.json#formdata json object receive
    number_of_qs = data["questionCount"] or 1
    if(CreateAssignment.validate_on_submit()):
        #access the question count field
        number_of_questions = 3
        #generate count many questions into a dictionary
        questions = generate_questions(count)
        #pass dicitonary object into template
        return render_template("index.html", questions=questions)

    #get questions from pipline
    questions = generate_questions(number_of_qs)
   #sample questions dictionary 
    #questions = {
    #     "1": {
    #         question:"",
    #         generated_answer:"",
    #         error_expected: int,
    #     },
    #     "2":{
    #         question:"",
    #         generated_answer:"",
    #         error_expected: int,
    #     },
    #     "2":{
    #         question:"",
    #         generated_answer:"",
    #         error_expected: int,
    #     },
    # }
    #to jsonify and pass into template
    return render_template('index.html', questions)


@app.route('/submit-assignment', methods=['POST'])
def submit_answers():
    feedback = {
        #in the same order as the answers were received
        #"1":"",#commment out once db is setup
        } 
    submit_form = Submit
    if(submit_form.validate_on_submit()):
        student_name = submit_form.student_name.data
        student_id = submit_form.student_id.data
        answers = {}
        index = 0
        for answer_tag in submit_form.answers:
            answers[f"{index}"] = answer_tag.data
        #add to intructor's respective assignment submissions column as table
        
    data = request.json
    answers = data.get('errorAnswers','')

    for i in range(len(answers)):
        feedback[f"{i}"] = (check_answer(answers[i]))
    jsonify(feedback)
    #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
    return "Successfully submitted!"

