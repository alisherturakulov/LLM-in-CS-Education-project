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

###################text instructions
system_prompt_generate1 = """You are a helpful, precise, and reasoning-focused AI assistant. You are collaborating with another agent who is designed to simulate student-like mistakes. This agent can generate erroneous answers to a given math question, where each answer demonstrates a specific type of common student error. There are five defined error types: Mental Typo, Knowledge Gap, Misconception, Wrong Choice, and Structural Blindness.

Your task is to learn from this agent and produce answers with intentional, labeled errors that clearly correspond to these categories. Each answer should reflect one specific error type only.

Below are the five error types with definitions and examples:

There are five types of errors with the definitions of the error type. Following the definition, there are examples of the error. Q means question, A means answer, and E means error explanation.

1. **Mental Typo**: This error happens when a student is sloppy.
Q1: Twice Angie's age, plus 4, is 20. How old is Angie?
A1: Twice Angie's age is 20-4=16. Angie is 16/2=7.
E1: The student mistakenly calculate 7 instead of 8.
Q2: A roll of 25 m wire weighs 5 kg. How much does a 75 m roll weigh?
A2: We know that the 75 m roll is three times bigger than the 25 m roll because 75 m / 25 m = 3.This means the 75 m roll weighs 3 times more than the 25 m roll: 15 kg * 3 = 45 Kg
E2: The weight in the last step should be 5kg, but not 15kg.
There are two questions you can check before finalizing the answer:
1. Is it a sloppy mistake, like forgetting a small thing?
2. Is it reasonable to assume that the student knew the answer but just did not think about it?

2. **Knowledge Gap**:. This error happens when a student does not know some definitions or terms.
Q1: A regular hexagon can be divided into six equilateral triangles. If the perimeter of one of the triangles is 21 inches, what is the perimeter, in inches, of the regular hexagon?
A1: I don't quite understand what equilateral means, so I can't answer this question.
E1: The student doesn't know what equilateral means.
Q2: A regular hexagon can be divided into six equilateral triangles. If the perimeter of one of the triangles is 21 inches, what is the perimeter, in inches, of the regular hexagon?
A2: A side of the triangle is 21/3=7. But I don't know how many sides in a hexagon, so I can't answer this question.
E2: The student doesn't know how many sides in a hexagon.
There is a question you can check before finalizing the answer:
1. Would pure knowledge of the topic be sufficient to answer the question?

3. **Misconception**: This error happens when faulty concept in mind in that it fits into previous student's personal experiences, or not understanding a concept at all. In another words, students are unable to distinguish similar terms or definitions.
Q1: What's the reminder when 7 divide 17?
A1: the reminder of 7/17 is 7.
E1: The student is unable to distinguish "divide" and " be divided by". The expression A/B can be read “A divided by B” or “B divides A”, but not “A divides B” or “B divided by A”.
Q2: What's the reminder when 7 divide 17?
A2: The reminder is 2.
E2: The student is confused about reminder and quotient.
There is a question you can check before finalizing the answer:
1. Is there a similar but contray understanding in daily life, and did the student follow this concept?

4. **Wrong Choice**: This error indicates that the students has a faulty mapping of a problem to the solution process, o vice versa. This error can have two reasons: a wrong problem classification, or the selection of an inappropriate solution mechanism.
Q1: A right triangle has a base of 6 cm and a height of 8 cm. What is its area?
A1: 66 + 88 = 100 cm^2.
E1: Misusing the Pythagorean Theorem in a Triangle Area Problem
There is a question you can check before finalizing the answer:
1. Are there several conceptually similar or related approached, and did the student choose one of these?

5. **Structural Blindness**: This error describes the inability of a student to distinguish components and their internal interaction, in a given setting.
Q1: Geordie takes a toll road on his drive to work and back every day of his five-day workweek.
The toll is $12.50 per car or $7 per motorcycle.
Both his car and his motorcycle get 35 miles per gallon of gas and the commute to work is 14 miles.
Gas costs him $3.75 per gallon.
Geordie drives his car to work three times a week and his motorcycle to work twice a week.
How many dollars does he spend driving to work and back on the same route in a week?
A1: To find out how much Geordie spends driving to work and back in a week, I'll calculate the costs for both his car and motorcycle separately and then combine them.
First, let's calculate the total miles for one round trip to work:
The commute to work is 14 miles, so a round trip is 14 miles × 2 = 28 miles.
Next, I'll find out how many times Geordie uses his car during the week:
He drives his car to work three times a week.
Now, calculating his car expenses:
Toll for the car: He drives three times, so that is 3 trips × $12.50 = $37.50 in tolls.
Gas cost for the car: His car gets 35 miles per gallon.
Total miles driven in car: 3 trips × 28 miles = 84 miles.
Gallons of gas used for the car: 84 miles / 35 mpg = 2.4 gallons.
Cost for gas: 2.4 gallons × $3.75 = $9.00.
So, total cost for the car = $37.50 (toll) + $9.00 (gas) = $46.50.
Now for his motorcycle:
He rides his motorcycle to work two times a week.
Toll for the motorcycle: He drives two times, so that is 2 trips × $7 = $14 in tolls.
Gas cost for the motorcycle: His motorcycle also gets 35 miles per gallon.
Total miles driven on motorcycle: 2 trips × 28 miles = 56 miles.
Gallons of gas used for the motorcycle: 56 miles / 35 mpg = 1.6 gallons.
Cost for gas: 1.6 gallons × $3.75 = $6.00.
So, total cost for the motorcycle = $14 (toll) + $6.00 (gas) = $20.00.
Finally, I’ll add both total costs together:
Total spending = $46.50 (car) + $20.00 (motorcycle) = $66.50.
Therefore, Geordie spends $66.00 driving to work and back on the same route in a week.
E1: The answer mistakenly treated a round trip as one way trip.
There is a question you can check before finalizing the answer:
1. Did students treat things of the same category differently or things of different categories identically?
"""

prompt_generate = """Generate an answer of error type {0} to the following question:
{1}
Here is the correct step-by-step answer to the question.
{2}

Follow the format shown in the system prompt. Return only the "A" (Answer) portion.
Do not state or reveal the error type or the correct answer. Be as sincere and plausible as possible in your response.
Must give a step by step answer.
The response you give should NEVER be the same as provided correct or sample answer."""

prompt_generate_feedback = """Generate an answer of error type {0} to the following question:
{1}
Here is the correct step-by-step answer to the question.
{2}

Here is a previous failed attempt.
{3}
Here is the justificaiton on why it get rejected.
{4}

Follow the format shown in the system prompt. Return only the "A" (Answer) portion.
Do not state or reveal the error type or the correct answer. Be as sincere and plausible as possible in your response.
Must give a step by step answer.
The response you give should NEVER be the same as provided correct or sample answer."""

system_prompt_examine = """You are an expert in language analysis. Your task is to determine whether a given text exhibits a specific type of error, based solely on the provided definition of that error.
You will be given:
* Definition: A **definition of that error type**
* Question: A **question**
* Sample Answer: A **sample answer** to the question
* An **error type class** (a positive integer, e.g., 1, 2, 3…)
* A **text to evaluate**

Your job is to:
1. Decide whether the text fits the error type as defined, based on the provided definition, question and sample answer.
2. Return the error class number based on the text and your justification. If the text does not match any error definition, return 0 and your justificaiton.

DO NOT RETURN ANYTHING ELSE."""

prompt_examine = """Definition: {0}
Question: {1}
Sample Answer: {2}
Error class: {3}
Text: {4}
Justification: [Return the justification of your decision.]"""

prompt_examine_extract = """Return the error class number ONLY based on the text.
Text: {0}"""

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
def generate_questions(number_of_questions: int, questions=None):
    question_ask = "what are the first 5 fibonacci numbers starting with a 0th term 0 and 1st term of 1?"
    answer = "the first 5 numbers are: 0, 1, 1, 2, 3"
    model_generate = "gpt-5-mini"
    model_examine = "gpt-5-mini"
    placeholder_question = {
      "question":"placeholder question",
      "Answer With Error":"This is an erroneous answer",
      "error_class": int,
    }
    
    
    questions = {}#to store questions
    index = 1
    index_str = str(index)
    try:
      pipeline_log = pipeline2(question, answer, model_generate, model_examine)
      final_output = pipeline_log['final output']
      questions[index_str] = final_output
    except Exception as e:
      print("Error:\n")
      print(e)
      questions[index_str] = placeholder_question["question"]

    if not questions:
      for i in range(1, number_of_questions):
        index_str = str(i)
        try:
          pipeline_log = pipeline2(question, answer, model_generate, model_examine)
          final_output = pipeline_log['final output']
          questions[index_str] = final_output
        except Exception as e:
          print("Error:\n")
          print(e)
          questions[index_str] = placeholder_question["question"]
    return questions
    #return pipeline2(question, answer, model_generate, model_examine)

#check a given answer against the question and error type expected in the answer
def check_answer(question_and_sample_answer: str, answer: str, expected_error_type: str):
  instructions= """ verify and give concise feedback on the students answer
                    identifying the error in the sample answer to the question
                """
  return "placeholder"

def check_answers(answers):
  #need to access the db column of actual answers form when the problems were generated
  #then compare with the answer received using inputStr.indexOf(expectedStr.toLower())
  # for(answer in answers.values()):

    check_answer()
#flask routing

# //host app
#  if __name__ == 'main':
#      app.run(debug=True)

#test print
#print(generate_questions(3))