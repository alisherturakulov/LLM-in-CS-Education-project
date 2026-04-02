#routing for flask project
from app import app
from flask import render_template, request, redirect, jsonify
from app.pipeline import check_answer, pipeline2, generate_questions
from app.forms import Login, Signup, CreateAssignment, Submit
#import db from module where initialized 

#holds the question_generated obj to be used to generate the assignment fillout
assignments = []
submissions = []
#submission= {"student_name":"", "student_id":"", "answers":[]}

idx = 0
# assignment = {idx : {
#     "question":"",
#     "expected_error":"",
#     "id":"",
# }}

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
        if(signup_form.validate_on_submit()):
            username = signup_form.username.data
            password = signup_form.password.data
            #make sure username's not a duplicate
            #store in db under new userid
        return redirect("/assign")
    
    return render_template('login.html', login_form=login_form, signup_form=signup_form)


@app.route('/assign', methods=['GET','POST'])
def create_questions():
    assign_form = CreateAssignment()
    #data = request.data.json#formdata json object receive
    #number_of_qs = data["questionCount"] or 1
    if(assign_form.validate_on_submit()):
        #access the question count field
        #number_of_questions = assign_form.number_of_questions.data;
        
        #should be a dict of dictionaries containing questionfield var_name: value for question text and 1-6 total error classes chosen
        questions_for_generating = assign_form.questions.data
        print("questions_for_generating: " + str(assign_form.questions.data))
        #shouls generate a list of dictionaries with
        generated_error_questions = generate_questions(questions_for_generating)
        print("Generated_error_questions:\n"+ str(generated_error_questions))
        #to be accessed later in /submit-assignment
        assignments.append(generated_error_questions)
        
        
        # questions = generate_questions(number_of_qs)
        #sample questions dictionary 
        # questions = {
        #     "1": {
        #         question:"question",
        #         generated_erranswer:"answer",
        #         error_expected: int,
        #     },
        #     "2":{
        #         question:"question",
        #         generated_erranswer:"answer",
        #         error_expected: int,
        #     },
        #     "2":{
        #         question:"question",
        #         generated_erranswer:"answer",
        #         error_expected: int,
        #     },
        # }
        #to jsonify and pass into template
        #put questions json into new assignment in assignments table of current instructor
        submit_form = Submit()
        assignment_id = len(assignments) - 1
        # return render_template("index.html", submit=submit_form, questions=zip(questions.items(), submit_form.answers))
        return redirect(f"/submit-assignment/{assignment_id}") #will access instructors db to allow sharing of some assignment
    return render_template("form-creator.html", form=assign_form)


@app.route('/submit-assignment/<int:assignment_id>', methods=['GET','POST'])
def submit_answers(assignment_id):
    feedback = {
        #in the same order as the answers were received
        #"1":"",#commment out once db is setup
        } 
    submit_form = Submit()
    #access latest created assignment from global object
    results = []
    current_assignment_dict = assignments[assignment_id]
    results_element= {"question":"", "answers":[],"expected":[]}
    if(submit_form.validate_on_submit()):
        student_name = submit_form.student_name.data
        student_id = submit_form.student_id.data
        answers = submit_form.answers.data
        answerIndex = 0
        #add to intructor's respective assignment submissions column as table
        #retrieve assignment index from redirect url, 
        #expected = []# for each answer in order from assignment in global assignments list variable { q: "", expected_error_class: ""} 
        #check each corresponding answer with expected error
        print(f"Answers:\n {answers}")
        for question_element in current_assignment_dict:
            for errorIndex in range(len(question_element["error classes"])):
                result = results_element
                result["question"] = question_element["question"]
                result["answers"].append(answers[answerIndex])
                result["expected"].append(question_element["error classes"][errorIndex])
                results.append(result)
                print(result)
                # index_str = str(index)
                # answers.append(submit_form.answer_tag.data)
                # expected[index_str] = assignments[assignment_id][error_classes]
                # feedback[index_str] = check_answer(submit_form.answer_tag.data)
                answerIndex += 1
                #answers_json = jsonify(answers)
                #feedback_json = jsonify(feedback)
                #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
        print('After adding:')
        print(results)
        return render_template_string(f"Successfully submitted!\nResults:\n{results}");
        #feedback = check_answers(answers)
    return render_template("index.html", submit=submit_form, questions_pair=list(zip(assignments[assignment_id], submit_form.answers)))

    # return "Error with submission"
    # data = request.json
    # answers = data.get('errorAnswers','')


@app.route("/share/<int:assignment_id>")
def share(assignment_id):#index from assignments list
    #assignment = assignments[assignment_id]
    return "will display assignments list, and redirect to a chosen submit-assignment/<int:assignment_index_in_list>"

@app.route("/submissions/<int:assignment_id>")
def submissions(assignment_id):
    submissions = ""
    for submission in submissions:
        results+= str(submission)
        results+= "\n"
    return submissions;
