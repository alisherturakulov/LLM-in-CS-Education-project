#routing for flask project
from app import app
from flask import render_template, request, jsonify
from pipeline import check_answer, pipeline2

@app.route('/')
@app.route('/index')
def home():
    #check db for authentication
    logged_in = True
    
    if (logged_in):
        render_template('form-creator.html')#uses jinja template engine
    else:
        return "error 401 incorrect credentials"

@app.route('/create-assignment', methods=['GET'])
def create_questions():
    data = request.json#formdata json object receive
    number_of_qs = data["questionCount"] or 1


    #get questions from pipline
    questions = generate_questions(number_of_qs)
   #sample questions dictionary 
    questions = {
        "1": {
            question:"",
            generated_answer:"",
            error_expected: int,
        },
        "2":{
            question:"",
            generated_answer:"",
            error_expected: int,
        },
        "2":{
            question:"",
            generated_answer:"",
            error_expected: int,
        },
    }#to jsonify and pass into template
    render_template('index.html', questions)


@app.route('/api/submit-assignment', methods=['POST'])
def submit_answers():
    feedback = {} #in the same order as the answers were received
    data = {}
    answers = data.get('errorAnswers','')
    for i in range(len(answers)):
        feedback.append(check_answer(answers[i]))
    jsonify(feedback)
    #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
    return "Successfully submitted!"

