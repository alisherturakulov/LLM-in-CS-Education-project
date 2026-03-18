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

//host app
if __name__ == 'main':
    app.run(debug=True)
    