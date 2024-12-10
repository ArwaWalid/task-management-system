import os
#important settings
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db' #help SQLAlchemy to know where to find or create the database file.
    SQLALCHEMY_TRACK_MODIFICATIONS = False #prevent un nesscary traking for optimization
    JWT_SECRET_KEY = 'secret_key' # secret key for encrypting and verifying tokens.
