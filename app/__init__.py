from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app) #thanks to https://flask-cors.corydolphin.com/en/2.0.1/

from app import routes