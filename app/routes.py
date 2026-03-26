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
    login_form = Login()
    signup_form = Signup()
    logged_in = Login.validate_on_submit()
    
    if (logged_in):
        return redirect('/assign')
    if(signup_form.validate_on_submit()):
        return redirect("/assign")
    
    return render_template('login.html', login_form=login_form, signup_form=signup_form)


@app.route('/assign', methods=['GET'])
def create_questions():
    assign_form = CreateAssignment()
    data = request.json#formdata json object receive
    number_of_qs = data["questionCount"] or 1
    if(CreateAssignment.validate_on_submit()):
        #access the question count field
        number_of_questions = 3
        #generate count many questions into a dictionary
        questions = generate_questions(count)
        #pass dicitonary object into template
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
        #put questions json into new assignment in assignments table of current instructor
        return redirect("index.html", questions=questions)
        #return redirect("index.html")
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
        for answer_tag in submit_form.answers.values():
            answers[f"{++index}"] = answer_tag.data
            feedback[f"{i}"] = (check_answer(answers[i]))
            #answers_json = jsonify(answers)
            #feedback_json = jsonify(feedback)
            #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
            return "Successfully submitted!"
        #feedback = check_answers(answers)
        #add to intructor's respective assignment submissions column as table
    return "error with submission"
    # data = request.json
    # answers = data.get('errorAnswers','')

    

