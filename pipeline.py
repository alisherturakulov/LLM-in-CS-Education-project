#will hold the data pipline that will run using flask to send a list of questions
#and then check the answers submitted by the user
import time
import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
from google import genai
from google.genai import types
from google import genai

#load from .env file
load_dotenv()

os.getenv('OPENAI_API_KEY') #from dotenv
os.getenv('GEMINI_API_KEY') 

#LLM client setup
clientOpenAI = OpenAI()

#list of error types ordered by index corresponding to that in pipline notebook
error_types = []

def generateGemini(prompt, model="gemini-2.0-flash"):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    if model == "gemini-2.0-flash":
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            response_mime_type="text/plain",
    )
    elif model in ["gemini-2.5-flash-preview-04-17", "gemini-2.5-pro-preview-05-06"]:
        generate_content_config = types.GenerateContentConfig(
          temperature=1.5,
          response_mime_type="text/plain",
      )
    else:
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=64,
            max_output_tokens=65536,
            response_mime_type="text/plain",
        )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config)
    return response.text

#generate OpenAI response using some model in response to some user content and system_prompt
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
def generate_questions(number_of_questions: int):
    # if(openAI.agent.is){

    # }
    question = ""
    answer = ""
    model_generate = ""
    model_examine = ""
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
    }
    return questions
    #return pipline2(question, answer, model_generate, model_examine)

#check a given answer against the question and error type expected in the answer
def check_answer(question_and_sample_answer: str, answer: str, expected_error_type: str):
  instructions= """ verify and give concise feedback on the students answer
                    identifying the error in the sample answer to the question
                """
  return ""

#flask routing

# //host app
#  if __name__ == 'main':
#      app.run(debug=True)
    