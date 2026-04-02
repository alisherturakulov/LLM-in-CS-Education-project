#routing for flask project
from app import app
from flask import render_template, request, redirect, render_template_string, jsonify
from app.pipeline import check_answer, pipeline2, generate_questions
from app.forms import Login, Signup, CreateAssignment, Submit
#import db from module where initialized 

#holds the question_generated obj to be used to generate the assignment fillout
assignments = []
submissions = []
results = []
#submission= {"student_name":"", "student_id":"", "answers":[]}

idx = 0
# assignment = {idx : {
#     "question":"",
#     "error answers":[],
#     "error classes":[],
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
        
        #to jsonify and pass into template
        #put questions json into new assignment in assignments table of current instructor
        
        assignment_id = len(assignments) - 1
        # return render_template("index.html", submit=submit_form, questions=zip(questions.items(), submit_form.answers))
        return redirect(f"./share/{assignment_id}") #will access instructors db to allow sharing of some assignment
    return render_template("form-creator.html", form=assign_form)


@app.route('/submit-assignment/<int:assignment_id>', methods=['GET','POST'])
def submit_answers(assignment_id):
    feedback = {
        #in the same order as the answers were received
        #"1":"",#commment out once db is setup
        } 
    submit_form = Submit()
    #access latest created assignment from global object
    assignment_results = []
    if isValidAssignment(assignment_id):
        current_assignment_dict = assignments[assignment_id]
    else:
        print("error: incorrect assignment_id in /submit")
        #raise IndexError("Incorrect assignment_id")
        return render_template_string("Error code 500 incorrect assignment id")
    
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
            result = {"question":"", "answers":[],"expected":[]}
            result["question"] = question_element["question"]
            for errorIndex in range(len(question_element["error classes"])):
                result["answers"].append(answers[answerIndex])
                result["expected"].append(question_element["error classes"][errorIndex])
                
                # index_str = str(index)
                # answers.append(submit_form.answer_tag.data)
                # expected[index_str] = assignments[assignment_id][error_classes]
                # feedback[index_str] = check_answer(submit_form.answer_tag.data)
                answerIndex += 1
                #answers_json = jsonify(answers)
                #feedback_json = jsonify(feedback)
                #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
            assignment_results.append(result)
            print(f"question result:{result}")
        print('After adding assignment_results:')
        print(assignment_results)
        return render_template_string(f"Successfully submitted!\nResults:\n{assignment_results}")
        #feedback = check_answers(answers)
    #create a list of generated answers
    
    erroneous_solutions = []
    corresponding_questions = []#list of str questions corresp. to their first erroroneous answer if "" dont print question
    for assignment in current_assignment_dict:
        for i  in range(len(assignment["error answers"])):
            error_answer = assignment["error answers"][i]
            if i == 0:
                corresponding_questions.append(assignment["question"])
            else: 
                corresponding_questions.append("")
            
            erroneous_solutions.append(error_answer)
            #answwers fieldlist should have length same as erroneous_solutions
            submit_form.answers.append_entry("")
    # if len(submit_form.answers.entries) != len(corresponding_questions):
        
    #     print(f"Error 500: lists of answerfields and corresponding questions don't match: {len(submit_form.answers.entries)} != {len(corresponding_questions)}")
    #     print(f"{submit_form.answers.entries}\n{corresponding_questions}")
    #     return render_template_string(f"Error 500: lists of answerfields and corresponding questions don't match: {len(submit_form.answers.entries)} != {len(corresponding_questions)}\n{submit_form.answers.entries}\n{corresponding_questions}")
    
    return render_template("index.html", submit=submit_form, corresponding_questions=corresponding_questions, questions_pair=zip(erroneous_solutions, submit_form.answers))

    # return "Error with submission"
    # data = request.json
    # answers = data.get('errorAnswers','')


@app.route("/share/<int:assignment_id>")
def share(assignment_id):#index from assignments list
    if isValidAssignment(assignment_id):
        current_assignment_dict = assignments[assignment_id]
    else:
        print("error: incorrect assignment_id in /submit")
        #raise IndexError("Incorrect assignment_id")
        return render_template_string("Error code 500 incorrect assignment id")
    #assignment = assignments[assignment_id]
    host = request.host_url
    return render_template("share.html", qrcode ="NA", assignment_id= assignment_id, host_url=request.host_url) or "will display assignments list, and redirect to a chosen submit-assignment/<int:assignment_index_in_list>"

@app.route("/submissions/<int:assignment_id>")
def submissions(assignment_id):
    #submissions is a global list
    if not isValidAssignment(assignment_id):
        print("error: incorrect assignment_id in /submit")
        #raise IndexError("Incorrect assignment_id")
        return render_template_string("Error code 500 incorrect assignment id")
    for submission in submissions:
        results+= str(submission)
        results+= "\n"
    return submissions;


def isValidAssignment(assignment_id):
    return assignment_id < len(assignments) and assignment_id >= 0
      
        