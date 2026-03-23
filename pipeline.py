#will hold the data pipline that will run using flask to send a list of questions
#and then check the answers submitted by the user
from flask import Flask, render_template, request, jsonify
import time
import os
from python-dotenv import load_dotenv
from openai import OpenAI

#load from .env file
load_dotenv()

os.environ['OPENAI_API_KEY'] = "your_api_key_here"#will use dotenv
clientOpenAI = OpenAI()


app = Flask(__name__)

#function to generate response from chosen openai model
def generatorOpenAI(content, model, system_prompt, temperature=1, reasoning_effort="high"):
  if model == "o3-mini":
    completion = clientOpenAI.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ],
        reasoning_effort=reasoning_effort
    )
  else:
      completion = clientOpenAI.chat.completions.create(
          model=model,
          temperature= temperature,
          messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
          ],
    )
  return completion

# Pipeline 2
# GA + EA
# 1) receive a question, generate its step by step sol (could have minor mistakes in it) (step by step answer is generated given correct answer)
# 2) generate a error type of the question
# 3) examine the generated type: if match, pass; otherwise, redo step3 till match
def pipeline2(question:str, answer:str, model_generate:str, model_examine:str):
  log = {str(error_class):None for error_class in range(1,6)}
  for error_class in range(1, 6): # error_class: int
    log[str(error_class)] = {"generation history": [], # list of str
                             "generation dialogue history": [],
                             "generation time history": [],
                             "generation input tokens history": [],
                             "generation output tokens history": [],
                             "generation reasoning tokens history": [],
                             "re-do counts": None, # int
                             "examination classification history": [],
                             "examination justification history": [],
                             "examination dialogue history": [],
                             "examination time history": [],
                             "examination input tokens history": [],
                             "examination output tokens history": [],
                             "examination reasoning tokens history": [],
                             "final output": None, # one single str
                             "final dialogue history": [],
                             "final output time": None,
                             "final input tokens": None,
                             "final output tokens": None,
                             "final reasoning tokens": None
                            }
    examination_result = "0"
    examination_feedback = ""
    while examination_result != str(error_class):
      # generate a type of a question
      time1 = time.time()
      if examination_feedback == "":
        generation_completion = generatorOpenAI(prompt_generate.format(str(error_class), question, answer), model_generate, system_prompt_generate1)
      else:
        generation_completion = generatorOpenAI(prompt_generate_feedback.format(str(error_class), question, answer, examination_result, examination_feedback), model_generate, system_prompt_generate1)
      time2 = time.time()
      generated_error_response = generation_completion.choices[0].message.content

      log[str(error_class)]['generation history'].append(generated_error_response)
      if examination_feedback == "":
        log[str(error_class)]['generation dialogue history'].append(prompt_generate.format(str(error_class), question, answer) + "\n\n" + generated_error_response)
      else:
        log[str(error_class)]['generation dialogue history'].append(prompt_generate_feedback.format(str(error_class), question, answer, examination_result, examination_feedback) + "\n\n" + generated_error_response)
      log[str(error_class)]['generation time history'].append(time2-time1)
      log[str(error_class)]['generation input tokens history'].append(generation_completion.usage.prompt_tokens)
      log[str(error_class)]['generation output tokens history'].append(generation_completion.usage.completion_tokens)
      log[str(error_class)]['generation reasoning tokens history'].append(generation_completion.usage.completion_tokens_details.reasoning_tokens)


      # examine the error class
      time3 = time.time()
      examination_completion = generatorOpenAI(prompt_examine.format(error_definitions_examine1, question, answer, str(error_class), generated_error_response), model_examine, system_prompt_examine)
      time4 = time.time()
      examination_justification = examination_completion.choices[0].message.content
      examination_result = generatorOpenAI(prompt_examine_extract.format(examination_justification), model_examine, "You're a useful agent on extracting information.").choices[0].message.content
      if examination_result != str(error_class):
        examination_feedback = examination_justification

      log[str(error_class)]['examination classification history'].append(examination_result)
      log[str(error_class)]['examination justification history'].append(examination_justification)
      log[str(error_class)]['examination dialogue history'].append(prompt_examine.format(error_definitions_examine1, question, answer, str(error_class), generated_error_response) + "\n\n" + examination_result)
      log[str(error_class)]['examination time history'].append(time4-time3)
      log[str(error_class)]['examination input tokens history'].append(examination_completion.usage.prompt_tokens)
      log[str(error_class)]['examination output tokens history'].append(examination_completion.usage.completion_tokens)
      log[str(error_class)]['examination reasoning tokens history'].append(examination_completion.usage.completion_tokens_details.reasoning_tokens)


      # take a break
      time.sleep(2)

    log[str(error_class)]['re-do counts'] = len(log[str(error_class)]['generation history'])-1
    log[str(error_class)]['final output'] = log[str(error_class)]['generation history'][-1]
    log[str(error_class)]['final dialogue history'] = log[str(error_class)]['generation dialogue history'][-1]
    log[str(error_class)]['final output time'] = log[str(error_class)]['generation time history'][-1]
    log[str(error_class)]['final input tokens'] = log[str(error_class)]['generation input tokens history'][-1]
    log[str(error_class)]['final output tokens'] = log[str(error_class)]['generation output tokens history'][-1]
    log[str(error_class)]['final reasoning tokens'] = log[str(error_class)]['generation reasoning tokens history'][-1]

    print(f"\r Error class {error_class} is done!", end="")
    time.sleep(1)

  return log 

#use pipeline from notebook
def send_question():
    return ""

def check_answer():
    return ""

#flask routing

@app.route('/')
def home():
    render_template('index.html')#uses jinja template engine

@app.route('/api/get_questions', methods=['GET'])
def get_questions():
    data = request.json
   
    questions = {}#to jsonify and send
    return jsonify(questions)

@app.route('/api/submit_answers', methods=['POST'])
def submit_answers():
    feedback = {} #in the same order as the answers were received
     answers = data.get('errorAnswers','')
    for i in range(len(answers)):
        feedback.append(check_answer(answers[i]))
    return jsonify(feedback)

# //host app
# if __name__ == 'main':
#     app.run(debug=True)
    