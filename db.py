
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
db = SQLAlchemy() #initializes SQLAlchemy
bcrypt = Bcrypt() # intializes Bcrypt
jwt = JWTManager() #intializes jwt

