########Project setup:
1.Download and install PyCharm from its official website.
2. Create a new folder to store all project files 
3. Install Required Libraries
pip install Flask            
pip install Flask-JWT-Extended 
pip install Flask-SQLAlchemy  
pip install Flask-Bcrypt     
pip install Flask-Mail        
4. Create Virtual Environment
5. Database Setup
      Download SQLite and connect it to the project.
      Use model.py to define the database schema.
      Use init_db.py to initialize the database
6. Configuration
Create a config.py file to store project configurations such as the database URI and email settings
7. Running the Application
        Start the Flask server locally: flask run
8. API Testing 
Download and use Postman for testing the API endpoints.
Import the Postman Collection JSON file for easy testing of all available routes.
9. Email Service Setup
The application uses Flask-Mail for sending emails:
        Set up a dedicated email account for the application.
        Enable SMTP access on the account.
        Generate an app-specific password.
        Update the email settings in config.py.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
postman collection link: https://x55555-2277.postman.co/workspace/9ed02964-179d-4925-bbd5-579874a795d7/documentation/40235878-cfae1363-5868-47f7-bfa6-be09a36a5313
it has a collection of all the requests and examples
the project folder has a postman collection json file 
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
####Project Structure 
1.	app.py => Main application file (entry point)
2.	config.py => Configuration Settings 
3.	db.py => Initializes SQLAlchemy, Bcrypt, and JWT 
4.	model.py => Defines database models
5.	int_db.py => Initializes the databas
6.	check_user.py => Check if a specific user exists in the database 
7.	auth.py => Handles user authentication and authorization
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Task report.pdf is a documentation for the task making has the relational database diagram, setup instrucyion, project structure , use case and testing api on postman steps and examples
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
