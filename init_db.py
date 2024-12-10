from app import app, db
with app.app_context():    # run the database creation within the Flask application
    db.create_all()        # Create all tables defined in the models
print("Database is created successfully!!!")
