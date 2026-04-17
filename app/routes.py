#routing for flask project
from app import app
from flask import render_template, request, redirect, render_template_string, url_for
from app.pipeline import check_answer, generate_questions, check_answers
from app.forms import Login, Signup, CreateAssignment, Submit
import os, json
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
                result["answers"].append(answers[answerIndex] if answerIndex < len(answers) else "")
                result["expected"].append(question_element["error classes"][errorIndex])
                # convert the log string into list-of-dicts per autosave snapshot
                raw_log = answer_logs[answerIndex] if answerIndex < len(answer_logs) else ""
                parsed = parse_log_string(raw_log)
                result["answer history"].append(parsed)
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
        # load the student's submissions file and show the saved entry for this assignment
        student_submissions = loadJSON("submissions.json", student_id)
        saved = None
        try:
            saved = student_submissions.get(str(assignment_id), {}).get(str(student_id))
        except Exception:
            saved = None
        return render_template_string(f"Successfully submitted! Saved: \n{saved}")
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
            # placeholder comments (feedback generation not implemented)
            comments = []
            erroneous_solutions.append(error_answer)
            #answwers fieldlist should have length same as erroneous_solutions
            submit_form.answers.append_entry("")
            submit_form.answer_logs.append_entry("")
    # if len(submit_form.answers.entries) != len(corresponding_questions):
        
    #     print(f"Error 500: lists of answerfields and corresponding questions don't match: {len(submit_form.answers.entries)} != {len(corresponding_questions)}")
    #     print(f"{submit_form.answers.entries}\n{corresponding_questions}")
    #     return render_template_string(f"Error 500: lists of answerfields and corresponding questions don't match: {len(submit_form.answers.entries)} != {len(corresponding_questions)}\n{submit_form.answers.entries}\n{corresponding_questions}")
    
    return render_template("index.html", submit=submit_form, corresponding_questions=corresponding_questions, questions_tuple=zip(erroneous_solutions, submit_form.answers, submit_form.answer_logs))

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

@app.route("/revise/<int:assignment_id>/<int:revision>", methods=['GET', 'POST'])
def revise(assignment_id, revision):
    submit_form = Submit()
    # load assignments and validate
    assignments = loadJSON("assignments.json")
    if not isValidAssignment(assignments, assignment_id):
        return render_template_string("Error code 500 incorrect assignment id")

    current_assignment_dict = assignments[assignment_id]

    # If a student_id is provided in query params, load their latest revisions/comments for display
    query_student = request.args.get('student_id')
    prefilled_comments = None
    if request.method == 'GET' and query_student:
        student_submissions = loadJSON('submissions.json', query_student) or {}
        existing_entry = {}
        try:
            existing_entry = student_submissions.get(str(assignment_id), {}).get(str(query_student), {})
        except Exception:
            existing_entry = {}

        # build flattened lists of erroneous answers and last-known comments (from most recent revision)
        all_erroneous = []
        all_comments = []
        for q in current_assignment_dict:
            for i, ea in enumerate(q.get('error answers', [])):
                all_erroneous.append(ea)
                # try to pull latest comment for this question+index from most recent revision
                comment = '(No comment)'
                try:
                    # look at latest revision entries in existing_entry['revisions'] (if any)
                    revs = existing_entry.get('revisions', []) if isinstance(existing_entry.get('revisions', []), list) else []
                    for rev in reversed(revs):
                        if rev.get('question','') == q.get('question',''):
                            cmts = rev.get('comments', [])
                            comment = cmts[i] if i < len(cmts) else comment
                            break
                except Exception:
                    comment = '(No comment)'
                all_comments.append(comment)

        # prepare form entries and render with comments
        submit_form = Submit()
        for _ in range(len(all_erroneous)):
            submit_form.answers.append_entry("")
            submit_form.answer_logs.append_entry("")
        corresponding_questions = []
        for q in current_assignment_dict:
            for i in range(len(q.get('error answers', []))):
                corresponding_questions.append(q.get('question','') if i==0 else "")
        return render_template('revise.html', submit=submit_form, corresponding_questions=corresponding_questions, questions_tuple=zip(all_erroneous, submit_form.answers, submit_form.answer_logs, all_comments))

    # prepare empty fields for the form based on generated erroneous solutions
    erroneous_solutions = []
    corresponding_questions = []
    for assignment in current_assignment_dict:
        for i in range(len(assignment.get("error answers", []))):
            error_answer = assignment["error answers"][i]
            if i == 0:
                corresponding_questions.append(assignment.get("question", ""))
            else:
                corresponding_questions.append("")
            erroneous_solutions.append(error_answer)
            submit_form.answers.append_entry("")
            submit_form.answer_logs.append_entry("")

    if request.method == 'POST':
        # Robust POST handling: accept raw form data even if WTForms validation fails
        student_name = request.form.get('student_name') or submit_form.student_name.data or ''
        student_id = request.form.get('student_id') or submit_form.student_id.data or ''

        # collect flat answers/logs from form fields named like answers-0, answers-1, ...
        flat_count = len(erroneous_solutions)
        answers = [request.form.get(f'answers-{i}', '') for i in range(flat_count)]
        answer_logs = [request.form.get(f'answer_logs-{i}', '') for i in range(flat_count)]

        answerIndex = 0
        result = None
        # load existing student submissions (if any) so we can compare prior attempts per question
        student_submissions = loadJSON("submissions.json", student_id) or {}
        existing_entry = {}
        try:
            existing_entry = student_submissions.get(str(assignment_id), {}).get(str(student_id), {})
        except Exception:
            existing_entry = {}

        # collect flattened lists for rendering after save
        all_erroneous = []
        all_comments = []

        for question_element in current_assignment_dict:
            result = {"name": student_name, "question": question_element.get("question", ""), "answers": [], "expected": [], "answer history": []}
            for errorIndex in range(len(question_element.get("error classes", []))):
                result["answers"].append(answers[answerIndex] if answerIndex < len(answers) else "")
                result["expected"].append(question_element["error classes"][errorIndex])
                result["answer history"].append(answer_logs[answerIndex] if answerIndex < len(answer_logs) else "")
                answerIndex += 1

            # find prior answers for THIS question (last revision for this question, or initial submission)
            prior_for_question = None
            try:
                # check revisions (most recent first)
                for rev in reversed(existing_entry.get('revisions', []) if isinstance(existing_entry.get('revisions', []), list) else []):
                    if rev.get('question','') == result['question']:
                        prior_for_question = rev.get('answers', [])
                        break
                # if no revisions, look for initial questions entry
                if prior_for_question is None:
                    for q in reversed(existing_entry.get('questions', []) if isinstance(existing_entry.get('questions', []), list) else []):
                        if q.get('question','') == result['question']:
                            prior_for_question = q.get('answers', [])
                            break
            except Exception:
                prior_for_question = None

            # call check_answers to generate comments for each answer for this question
            try:
                comments_for_q = check_answers(result.get('answers', []), [question_element], prior_answers=prior_for_question)
            except Exception:
                # fallback to placeholders
                comments_for_q = ["(No comments generated)" for _ in result.get('answers', [])]

            # attach comments to revision entry
            revision_entry = {
                'name': result.get('name',''),
                'question': result.get('question',''),
                'answers': result.get('answers',[]),
                'expected': result.get('expected',[]),
                'answer history': result.get('answer history',[]),
                'comments': comments_for_q
            }
            add_revision(assignment_id, student_id, revision_entry)

            # collect for rendering
            for i, ea in enumerate(question_element.get('error answers', [])):
                all_erroneous.append(ea)
                # each erroneous answer corresponds to an entry in comments_for_q (if lengths align)
                c = comments_for_q[i] if i < len(comments_for_q) else "(No comment)"
                all_comments.append(c)

        # redirect to GET (Post-Redirect-Get) so browser won't re-submit repeatedly
        # include student_id so GET can display the just-saved comments
        return redirect(request.path + f"?student_id={student_id}")

    # provide a comments list (empty) so template can unpack 4 items
    comments = ["(No comments yet)"] * len(erroneous_solutions)
    return render_template("revise.html", submit=submit_form, corresponding_questions=corresponding_questions, questions_tuple=zip(erroneous_solutions, submit_form.answers, submit_form.answer_logs, comments))

def isValidAssignment(assignments: list, assignment_id: int):
    return isinstance(assignments, list) and assignment_id < len(assignments) and assignment_id >= 0


def parse_log_string(log_str: str):
    """Parse a log string like "TIME : value;TIME2 : value2;" into a list of {time: value} dicts."""
    if not log_str:
        return []
    items = []
    for part in log_str.split(';'):
        token = part.strip()
        if not token:
            continue
        # look for first ' : ' separator
        if ' : ' in token:
            time, val = token.split(' : ', 1)
            items.append({time.strip(): val.strip()})
        else:
            # fallback: store whole token with empty key
            items.append({"": token})
    return items


def add_revision(assignment_id: int, student_id: str, revision_entry: dict, dataFileName: str = 'submissions.json'):
    """Append a revision_entry to student file under assignment_id -> student_id -> revisions (list).
    Creates student file and assignment slot if missing.
    """
    current_filepath = os.path.dirname(__file__)
    base_path = os.path.join(current_filepath, os.pardir, "data")
    filepath = os.path.join(base_path, dataFileName)
    student_dir = os.path.join(base_path, 'students', str(student_id))
    os.makedirs(student_dir, exist_ok=True)
    student_file = os.path.join(student_dir, dataFileName)
    # ensure student file exists by copying base or creating empty
    if not os.path.exists(student_file):
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as src, open(student_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        else:
            with open(student_file, 'w', encoding='utf-8') as dst:
                json.dump({}, dst)

    try:
        with open(student_file, 'r', encoding='utf-8') as f:
            dataObject = json.load(f)
    except Exception:
        dataObject = {}

    if str(assignment_id) not in dataObject:
        dataObject[str(assignment_id)] = {}

    student_map = dataObject[str(assignment_id)]
    sid = str(student_id)
    if sid not in student_map or not isinstance(student_map[sid], dict):
        # initialize
        student_map[sid] = {"name": revision_entry.get('name',''), "questions": [], "revisions": []}

    student_entry = student_map[sid]
    student_entry.setdefault('revisions', []).append(revision_entry)

    with open(student_file, 'w', encoding='utf-8') as f:
        json.dump(dataObject, f, indent=4)
    return True
      
def addToJSON(dataToAdd, dataFileName, assignments=True, assignment_id=-1, student_id=-1):
    """Add dataToAdd to data/<dataFileName>.
    - If assignments=True: treat the file as a list and append, return new length.
    - If assignments=False: treat the file as submissions dict and write under [assignment_id][student_id].
    When writing student-specific submissions, ensure data/students/<student_id>/submissions.json exists; if not, copy data/submissions.json into the student's directory.
    """
    dataLength = -1
    current_filepath = os.path.dirname(__file__)
    base_path = os.path.join(current_filepath, os.pardir, "data")
    filepath = os.path.join(base_path, dataFileName)

    try:
        # ensure base file exists
        if not os.path.exists(filepath):
            # create an empty list or dict depending on assignments
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump([] if assignments else {}, f)

        # if writing student-specific submissions, ensure student folder and file
        if not assignments and student_id is not None and str(student_id) != "":
            student_dir = os.path.join(base_path, 'students', str(student_id))
            os.makedirs(student_dir, exist_ok=True)
            student_file = os.path.join(student_dir, dataFileName)
            if not os.path.exists(student_file):
                # copy base submissions file into student dir if it exists, otherwise create empty structure
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as src, open(student_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                else:
                    with open(student_file, 'w', encoding='utf-8') as dst:
                        json.dump({}, dst)

        # choose target file
        target_file = filepath
        if not assignments and student_id is not None and str(student_id) != "":
            target_file = os.path.join(base_path, 'students', str(student_id), dataFileName)

        # load existing data
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                dataObject = json.load(f)
        except Exception:
            dataObject = [] if assignments else {}

        if assignments:
            if not isinstance(dataObject, list):
                raise ValueError('Expected assignments file to contain a list')
            dataObject.append(dataToAdd)
            dataLength = len(dataObject)
        else:
            if assignment_id < 0 or student_id is None or str(student_id) == "":
                raise ValueError('addToJSON: assignment_id or student_id incorrect')
            # ensure assignment slot exists
            if str(assignment_id) not in dataObject:
                dataObject[str(assignment_id)] = {}
            student_map = dataObject[str(assignment_id)]
            sid = str(student_id)
            # if student already has an entry, try to preserve/append to 'questions' list
            if sid in student_map and isinstance(student_map[sid], dict):
                existing = student_map[sid]
                # if existing uses flat format (has 'question'), convert to questions list
                if 'questions' not in existing and any(k in existing for k in ('question','answers')):
                    qobj = {
                        'question': existing.get('question',''),
                        'answers': existing.get('answers',[]),
                        'expected': existing.get('expected',[]),
                        'answer history': existing.get('answer history',[])
                    }
                    existing = {'name': existing.get('name',''), 'questions':[qobj], 'revisions': existing.get('revisions',{})}
                    student_map[sid] = existing
                # append new question entry
                qentry = {
                    'question': dataToAdd.get('question',''),
                    'answers': dataToAdd.get('answers',[]),
                    'expected': dataToAdd.get('expected',[]),
                    'answer history': dataToAdd.get('answer history',[])
                }
                existing.setdefault('questions',[]).append(qentry)
            else:
                # create new student entry with questions list
                student_map[sid] = {
                    'name': dataToAdd.get('name',''),
                    'questions': [{
                        'question': dataToAdd.get('question',''),
                        'answers': dataToAdd.get('answers',[]),
                        'expected': dataToAdd.get('expected',[]),
                        'answer history': dataToAdd.get('answer history',[])
                    }],
                    'revisions': {}
                }
            dataLength = len(dataObject)

        # write back
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(dataObject, f, indent=4)
    except Exception as e:
        print(e)
        dataLength = -1

    return dataLength


def loadJSON(dataFileName, student_id: int = None):
    """Load a JSON file from data/ or data/students/<student_id>/ when student_id provided."""
    current_filepath = os.path.dirname(__file__)
    base_path = os.path.join(current_filepath, os.pardir, "data")
    filepath = os.path.join(base_path, dataFileName)

    if student_id is not None and str(student_id) != "":
        student_file = os.path.join(base_path, 'students', str(student_id), dataFileName)
        if os.path.exists(student_file):
            filepath = student_file

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            dataObject = json.load(f)
            return dataObject
    except Exception as e:
        print(e)
        return None

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
