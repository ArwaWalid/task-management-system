from flask import Blueprint, request, jsonify
from db import db, bcrypt, jwt
from flask_jwt_extended import create_access_token
from models import User  # Ensure that the User model is imported

auth_blueprint = Blueprint('auth', __name__)

# Sign up route
@auth_blueprint.route('/signup', methods=['POST'])   # Create /signup path for POST requests
def signup():          # fn that will be executed when a POST request is made (/signup)
    data = request.get_json()  #Extract data from the json request
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    # Hash the password and convert the byte string to a regular string to be stored in database
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User.query.filter_by(email=email).first()   #Query database to check that email not already exist
    if user:    #not none
        return jsonify({"message": "Email already exists!"}), 400   #status code 400 ~ bad request
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit() #create a new user and save to database
    return jsonify({"message": "User registered successfully!"}), 201 #status code 201 ~ Created

# Sign in route
@auth_blueprint.route('/signin', methods=['POST']) # Create /signin path for POST requests
def signin():
    data = request.get_json() # Extract JSON data from the request
    #retrive email and password fields from json data
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first() #Query the database to find a user with the provided email.
    # Checks if the user exists and verifies the password matches the stored hash
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id)) #Creates a JWT using the user's ID for authentication
        return jsonify({"message": "Signin successful!", "access_token": access_token}), 200 #status code 200 ~ OK
    else:
        return jsonify({"message": "Invalid credentials!"}), 401 #status code 200 ~ Un authorized
