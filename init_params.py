from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import configparser
cf=configparser.ConfigParser()
cf.read('config.ini')
sql_type = cf.get("database", "sql_type")
host = cf.get("database", "host")
port = cf.get("database", "port")
username = cf.get("database", "username")
password = cf.get("database", "password")
database = cf.get("database", "database")

app = Flask(__name__)

CORS(app, supports_credentials=True)



app.config[
    'SQLALCHEMY_DATABASE_URI'] = '%s://%s:%s@%s:%s/%s?charset=utf8' %(sql_type,username,password,host,port,database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
