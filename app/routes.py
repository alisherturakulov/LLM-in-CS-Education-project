#routing for flask project
from app import app
from flask import render_template, request, redirect, jsonify
from app.pipeline import check_answer, pipeline2, generate_questions
from app.forms import Login, Signup, CreateAssignment, Submit
#import db from module where initialized 



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def home():
    #check db for authentication
    login_form = Login()
    signup_form = Signup()
    
    if (request.method=="POST"):
        if(login_form.validate_on_submit()):
            username = login_form.username.data
            password= login_form.password.data
            remember_me = login_form.remember_me.data
            #in db match password hashed with the stored password hash under instructor_id with this username
            return redirect('/assign')
        if(signup_form.validate_on_submit()):
            username = signup_form.username.data
            password = signup_form.password.data
            #make sure username's not a duplicate
            #store in db under new userid
            return redirect("/assign")
    
    return render_template('login.html', login_form=login_form, signup_form=signup_form)


@app.route('/assign', methods=['POST'])
def create_questions():
    assign_form = CreateAssignment()
    #data = request.data.json#formdata json object receive
    #number_of_qs = data["questionCount"] or 1
    if(assign_form.validate_on_submit()):
        #access the question count field
        number_of_questions = assign_form.number_of_questions.data;
        #generate count many questions into a dictionary
        # questions = generate_questions(count)
        #pass dicitonary object into template
        #get questions from pipline
        # questions = generate_questions(number_of_qs)
        #sample questions dictionary 
        questions = {
            "1": {
                question:"question",
                generated_erranswer:"answer",
                error_expected: int,
            },
            "2":{
                question:"question",
                generated_erranswer:"answer",
                error_expected: int,
            },
            "2":{
                question:"question",
                generated_erranswer:"answer",
                error_expected: int,
            },
        }
        #to jsonify and pass into template
        #put questions json into new assignment in assignments table of current instructor
        return render_template("index.html", questions=questions)
        #return redirect("index.html") #will access instructors db to allow sharing of some assignment
    return render_template("form-creator.html", form=assign_form)


@app.route('/submit-assignment', methods=['POST'])
def submit_answers():
    feedback = {
        #in the same order as the answers were received
        #"1":"",#commment out once db is setup
        } 
    submit_form = Submit()
    answers = {}
    if(submit_form.validate_on_submit()):
        student_name = submit_form.student_name.data
        student_id = submit_form.student_id.data
        answers = {}
        index = 0
        for answer_tag in submit_form.answers.data:
            answers[f"{++index}"] = submit_form.answer_tag
            feedback[f"{i}"] = check_answer(submit_form.answer_tag)
            #answers_json = jsonify(answers)
            #feedback_json = jsonify(feedback)
            #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
            return "Successfully submitted!"
        #feedback = check_answers(answers)
        #add to intructor's respective assignment submissions column as table
    return "error with submission"
    # data = request.json
    # answers = data.get('errorAnswers','')

    

