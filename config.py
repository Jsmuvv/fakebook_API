import os
from dotenv import load_dotenv

load_dotenv()
#  Get the path to the base directory 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG')