import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:aditya%40168@localhost/intern'
    SQLALCHEMY_TRACK_MODIFICATIONS = False