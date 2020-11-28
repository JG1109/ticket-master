# imports
from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy

# initializing Flask app
app = Flask(__name__)

# GCP SQL
PASSWORD = "password"
PUBLIC_IP_ADDRESS = "xxx.xxx.xxx.xxx"
DBNAME = "data base name"
PROJECT_ID = "project id"
INSTANCE_NAME = "instance name"

# configuration
app.config["SECRET_KEY"] = "Ticket Master!"
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql + mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket =/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
