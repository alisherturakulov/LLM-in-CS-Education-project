# #app variable

from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes#to deal with circular imports

#todo: init database to store form data from routes