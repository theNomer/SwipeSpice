import os

class Config:
    username = ''
    password = ''
    database = 'swipeandspice'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'postgresql://{username}:{password}@localhost:5432/{database}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)  # Generates a random secret key

    # flask db init
    # flask db migrate -m "Initial migration."
    # flask db upgrade
