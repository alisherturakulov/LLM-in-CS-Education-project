#routing for flask project
from app import app
from flask import render_template, request, jsonify
from pipeline import check_answer, pipeline2

#import db from module where initialized 



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
    #check db for authentication
    
    logged_in = True
    
    if (logged_in):
        return render_template('form-creator.html')#uses jinja template engine
    else:
        return render_template('login.html')


@app.route('/create-assignment', methods=['GET'])
def create_questions():
    data = request.json#formdata json object receive
    number_of_qs = data["questionCount"] or 1


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


@app.route('/api/submit-assignment', methods=['POST'])
def submit_answers():
    feedback = {
        #in the same order as the answers were received
        #"1":"",#commment out once db is setup
        } 
    data = request.json
    answers = data.get('errorAnswers','')
    for i in range(len(answers)):
        feedback.append(check_answer(answers[i]))
    jsonify(feedback)
    #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
    return "Successfully submitted!"

