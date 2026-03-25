# #app variable

from flask import Flask

app = Flask(__name__)

from app import routes#to deal with circular imports