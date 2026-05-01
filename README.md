# LLMs in CS Education project


## Setup
Requirements: Python3 and Flask

Clone the repository into a new directory

Install dependencies from requirements.txt
```bash
pip install -r requirements.txt
```

```bash
#Create a .env file:
touch .env
echo "FLASK_APP=tasksystem.py" >> .env
#password used by instructor to access create, share, and view pages
echo "ADMIN_PIN=<admin login goes here>" >> .env
#use openai for comments
echo "COMMENT_USE_OPENAI=1" >> .env
#api keys, functions can use either
echo "OPENAI_API_KEY=<api key>" >> .env
echo "GEMINI_API_KEY=<api key>" >> .env
```

Run the flask server (localhost)
```bash
flask run
```

#Instructors run flask from 0.0.0.0 to allow other devices to access submit and #revise routes
```bash
#hosts on all addresses
flask run --host 0.0.0.0
#ctrl-C to stop
```