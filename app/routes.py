#routing for flask project
from app import app
from flask import render_template, request, redirect, render_template_string
from app.pipeline import check_answer, generate_questions
from app.forms import Login, Signup, CreateAssignment, Submit
import os, json, portalocker
#import db from module where initialized, use data folder json for now

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
        #assignments.append(generated_error_questions)
        
        #takes care of file locking concurrency, appends to exisiting data in file
        newLength = addToJSON(generated_error_questions, "assignments.json")
        # questions = generate_questions(number_of_qs)
        if (newLength <= 0):
            return render_template_string("Error 500: in create, error appending assignment")
        #to jsonify and pass into template
        #put questions json into new assignment in assignments table of current instructor
        
        assignment_id = newLength - 1
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
    assignments = loadJSON("assignments.json")
    if isValidAssignment(assignments, assignment_id):
        current_assignment_dict = assignments[assignment_id]
    else:
        print("error: incorrect assignment_id in /submit")
        #raise IndexError("Incorrect assignment_id")
        return render_template_string("Error code 500 incorrect assignment id")
    
    if(submit_form.validate_on_submit()):
        student_name = submit_form.student_name.data
        student_id = submit_form.student_id.data
        answers = submit_form.answers.data
        answer_logs = submit_form.answer_logs.data
        print(f"#########answer logs:\n {answer_logs}")
        answerIndex = 0
        #add to intructor's respective assignment submissions column as table
        #retrieve assignment index from redirect url, 
        #expected = []# for each answer in order from assignment in global assignments list variable { q: "", expected_error_class: ""} 
        #check each corresponding answer with expected error
        print(f"Answers:\n {answers}")
        for question_element in current_assignment_dict:
            result = {"name":"", "question":"", "answers":[],"expected":[], "answer history":[]}
            result["name"] = student_name
            result["question"] = question_element["question"]
            for errorIndex in range(len(question_element["error classes"])):
                result["answers"].append(answers[answerIndex])
                result["expected"].append(question_element["error classes"][errorIndex])
                result["answer history"].append(answer_logs[answerIndex])
                # index_str = str(index)
                # answers.append(submit_form.answer_tag.data)
                # expected[index_str] = assignments[assignment_id][error_classes]
                # feedback[index_str] = check_answer(submit_form.answer_tag.data)
                answerIndex += 1
                #answers_json = jsonify(answers)
                #feedback_json = jsonify(feedback)
                #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
            newSubmissionsLength = addToJSON(result, "submissions.json", False, assignment_id, student_id)
            #assignment_results.append(result)
            print(f"question result:{result}")
        submissions = loadJSON("submissions.json")
        
        print('After adding result to submissions:')
        print(f"{newSubmissionsLength}\n{submissions}")
        return render_template_string(f"Successfully submitted!Submissions: \n{submissions}")
        #feedback = check_answers(answers)
    #create a list of generated answers
    comments = []
    erroneous_solutions = []
    corresponding_questions = []#list of str questions corresp. to their first erroroneous answer if "" dont print question
    for assignment in current_assignment_dict:
        for i  in range(len(assignment["error answers"])):
            error_answer = assignment["error answers"][i]
            if i == 0:
                corresponding_questions.append(assignment["question"])
            else: 
                corresponding_questions.append("")
            comments = generate_feedback(zip(answers, expected))
            erroneous_solutions.append(error_answer)
            #answwers fieldlist should have length same as erroneous_solutions
            submit_form.answers.append_entry("")
            submit_form.answer_logs.append_entry("")
    # if len(submit_form.answers.entries) != len(corresponding_questions):
        
    #     print(f"Error 500: lists of answerfields and corresponding questions don't match: {len(submit_form.answers.entries)} != {len(corresponding_questions)}")
    #     print(f"{submit_form.answers.entries}\n{corresponding_questions}")
    #     return render_template_string(f"Error 500: lists of answerfields and corresponding questions don't match: {len(submit_form.answers.entries)} != {len(corresponding_questions)}\n{submit_form.answers.entries}\n{corresponding_questions}")
    
    return render_template("index.html", submit=submit_form, corresponding_questions=corresponding_questions, questions_tuple=zip(erroneous_solutions, submit_form.answers, submit_form.answer_logs, comments))

    # return "Error with submission"
    # data = request.json
    # answers = data.get('errorAnswers','')


@app.route("/share/<int:assignment_id>")
def share(assignment_id):#index from assignments list
    assignments = loadJSON("assignments.json")
    if isValidAssignment(assignments, assignment_id):
        current_assignment_dict = assignments[assignment_id]
    else:
        print("error: incorrect assignment_id in /submit")
        #raise IndexError("Incorrect assignment_id")
        return render_template_string("Error code 500 incorrect assignment id")
    #assignment = assignments[assignment_id]
    host = request.host_url
    return render_template("share.html", assignment_id= assignment_id, host_url=request.host_url) or render_template_string("will display assignments list, and redirect to a chosen submit-assignment/<int:assignment_index_in_list>")

@app.route("/submissions/<int:assignment_id>")
def submissions(assignment_id):
    #submissions json
    results = ""
    submissions = loadJSON("submissions.json")
    assignments = loadJSON("assignments.json")
    if not isValidAssignment(assignments, assignment_id):
        print("error: incorrect assignment_id in /submit")
        #raise IndexError("Incorrect assignment_id")
        return render_template_string("Error code 500 incorrect assignment id")
    for student_id in submissions[assignment_id].keys():
            results+= f"\nStudent_id {student_id}:\n{submissions[assignment_id][student_id]}"
            results+= "\n"
    return render_template_string(results)

@app.route("/revise/<int:assignment_id>/<int:revision>")
def revise(assignment_id, revision):
    revised_assignment = {
        "question": "",
        "answers": [""],
        "expected": [""],
        "comments":[""],
        "answer history": ["<time>:<input>;"]
    } 
    submit_form = Submit()
    #access latest created assignment from global object
    assignment_results = []
    assignments = loadJSON("assignments.json")
    if isValidAssignment(assignments, assignment_id):
        current_assignment_dict = assignments[assignment_id]
    else:
        print("error: incorrect assignment_id in /submit")
        #raise IndexError("Incorrect assignment_id")
        return render_template_string("Error code 500 incorrect assignment id")
    
    if(submit_form.validate_on_submit()):
        student_name = submit_form.student_name.data
        student_id = submit_form.student_id.data
        answers = submit_form.answers.data
        answer_logs = submit_form.answer_logs.data
        print(f"#########answer logs:\n {answer_logs}")
        answerIndex = 0
       
        for question_element in current_assignment_dict:
            result = {"name":"", "question":"", "answers":[],"expected":[], "answer history":[]}
            result["name"] = student_name
            result["question"] = question_element["question"]
            for errorIndex in range(len(question_element["error classes"])):
                result["answers"].append(answers[answerIndex])
                result["expected"].append(question_element["error classes"][errorIndex])
                
                answerIndex += 1
                
                #add answers to instructor_id's specific assignment's submissions table (see PROTOTYPE.md)
            newSubmissionsLength = addToJSON(result, "submissions.json", False, assignment_id, student_id)
            #assignment_results.append(result)
            print(f"question result:{result}")
        submissions = loadJSON("submissions.json")
        
        print('After adding result to submissions:')
        print(f"{newSubmissionsLength}\n{submissions}")
        return render_template_string(f"Successfully submitted!Submissions: \n{result}")
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
            submit_form.answer_logs.append_entry("")
    
    return render_template("revise.html", submit=submit_form, corresponding_questions=corresponding_questions, questions_tuple=zip(erroneous_solutions, submit_form.answers, submit_form.answer_logs))

def isValidAssignment(assignments: list, assignment_id: int):
    return assignment_id < len(assignments) and assignment_id >= 0
      

def addToJSON(dataToAdd, student_id: int, assignment_id: int, revise = False):
    try:
        os.system(f"ls {os.path.join(os.path.dirname(__file__), os.pardir, "data", "students", str(student_id))}")
    except FileNotFoundError as e:
        #make the id directory if it doesnt exist
        os.mkdir(os.path.join(os.path.dirname(__file__), os.pardir, "data", "students", str(student_id)))

    
    try:
        #add submission or to an exisitng submission to students/student_id/submissions/submissions.json
        with open(os.path.join(os.path.dirname(__file__), os.pardir, "data", "students", str(student_id), "submissions.json")) as f:
            data = json.load(f)
            data[str(assignment_id)] = dataToAdd
    except (Exception) as e:    
        print(f"error in addToJSON{e}")
        return False
    finally:
        return True

def loadJSON(student_id: int, assignment_id:int):
    try:
        os.system(f"ls {os.path.join(os.path.dirname(__file__), os.pardir, "data", "students", str(student_id))}")
    except FileNotFoundError as e:
        #make the id directory if it doesnt exist
        os.mkdir(os.path.join(os.path.dirname(__file__), os.pardir, "data", "students", str(student_id)))
    
    assignment = None
    try:
        #load from the student id directories submissions.json
        with open(os.path.join(os.path.dirname(__file__), os.pardir, "data", "students", str(student_id), "submissions.json")) as f:
            data = json.load(f)
            assignment = data[str(assingment_id)]
    except (Exception) as e:
        print(f"error in loadJSON{e}")
    finally:
        return assignment

#def addToJSON(dataToAdd, dataFileName, assignments=True, assignment_id=-1, student_id=-1):
#     #with filelocking save given json data to specified filepath 
#     dataLength = 0
#     current_filepath = os.path.dirname(__file__)
#     filepath= os.path.join(current_filepath, os.pardir, "data", dataFileName)
#     print(f"path before adding: {filepath}")
#     try:
#         #with open(filepath, 'r+', encoding="utf-8") as file:
#         #preventing concurrent saves using file lock
#         with portalocker.Lock(filepath, mode="r+", timeout=7, encoding="utf-8") as f:
#             #load the object and check whether its assignments(list) or submissions(dictionary)
#             dataObject = json.load(f)
#             if (assignments):#if adding to list (assignments.json)
#                 dataObject.append(dataToAdd)
#                 dataLength = len(dataObject)
#             else:#if adding to dictionary (submissions)
#                 if(assignment_id < 0 or int(student_id) < 0):
#                     print("addToJSON error: assignment_id or student_id incorrect")
#                     raise ValueError("addToJSON assingment_id or student_id incorrect")
#                 if(str(assignment_id) not in dataObject):
#                     dataObject[str(assignment_id)] = {}
#                 dataObject[str(assignment_id)][student_id] = dataToAdd
#             f.seek(0)#back to start of file
#             json.dump(dataObject, f, indent=4)
#             f.truncate()#cuts extra data if dataObject is shorter
#             f.flush()
#     except (OSError, TypeError, ValueError, Exception) as e:
#         print(e)
#         dataLength = -1
        
#     return dataLength
#         # finally:
#         #     portalocker.unlock(f)#unlock once done

# def loadJSON(dataFileName):
#     #with filelocking return a object as a list or dict froom data file
#     dataObject = None
#     try:
#         current_filepath = os.path.dirname(__file__)
#         filepath = os.path.join(current_filepath, os.pardir,"data", dataFileName)
#         #with open(filepath, "r", encoding="utf-8") as f:
#         with portalocker.Lock(filepath, mode="r", timeout=7, encoding="utf-8") as f: 
#         #automatically uses LOCK_EX
#         #preventing concurrent saves using file lock
#             dataObject = json.load(f)
#     except (OSError, TypeError) as e:
#         print(e)
#     return dataObject
