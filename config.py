import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = '12345' 
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False