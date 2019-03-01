# import os
# basedir = os.path.abspath(os.path.dirname(__file__))
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db?check_same_thread=False')

# General Keys
ENV = 'development'
DEBUG = True
SECRET_KEY = 'a-key'
# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@localhost:3306/databasename'
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = False

# pip freeze > requirements.txt
