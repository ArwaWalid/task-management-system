from app import app, db
from models import User

# Check if the user exists
with app.app_context():
    user = User.query.filter_by(email="testuser@example.com").first()
    if user:
        print(f"User found: {user.username}, {user.email}")
    else:
        print("User not found!!")
