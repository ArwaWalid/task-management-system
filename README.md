####Task report.pdf is a documentation for the task and comprehensive details about the project, including the relational database diagram, setup instruction, project structure , use case and testing api on postman steps and examples


#####postman collection link: https://x55555-2277.postman.co/workspace/9ed02964-179d-4925-bbd5-579874a795d7/documentation/40235878-cfae1363-5868-47f7-bfa6-be09a36a5313
it has a collection of all the requests and examples
the project folder has a postman collection json file 

#####Project setup:
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




####Project Structure 
1.	app.py => Main application file (entry point)
2.	config.py => Configuration Settings 
3.	db.py => Initializes SQLAlchemy, Bcrypt, and JWT 
4.	model.py => Defines database models
5.	int_db.py => Initializes the databas
6.	check_user.py => Check if a specific user exists in the database 
7.	auth.py => Handles user authentication and authorization



#### to test signup API
1.	Open Postman
2.	Select POST request type
3.	Enter endpoint url: http://localhost:5000/signup
4.	Navigate to the Body tab then select raw data type and choose JSON format
5.	Enter JSON data in the body
{
 "username": "user", 
 "email": "user@example.com",
 "password": "Password" 
}
6.	Send the Request
7.	Verify the Response 
For successful registration, the response should include the message 
"User registered successfully!" with a 201 status code.
If the user is already registered, the response should return a message like "Email already exists!" with a 400 status code.




#### to test signin API 
1.	Open Postman
2.	Select POST request type
3.	Enter endpoint url: http://127.0.0.1:5000/signin
4.	Navigate to the Body tab then select raw data type and choose JSON format
5.	Enter JSON data in the body
{
 "username": "user", 
 "email": "user@example.com",
 "password": "Password" 
}
6.	Send the Request
7.	Verify the Response 
For successful sign-in, the response should include the message "Signin successful!" and an access_token (JWT) generated for the user with a 200 status code.
For invalid credentials, the response should return the message "Invalid credentials!" with a 401 status code.




#### to test createtask API
1.	Open Postman
2.	Select POST request type
3.	Enter endpoint url: http://127.0.0.1:5000/createtask
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	Navigate to the Body tab then select raw data type and choose JSON format
7.	Enter JSON data in the body
{
    "title"  : "Task",
    "description"  : "TaskDescription",
    "start_date"  : "2024-12-10T17:30:00Z",
    "due_date"  :  "2024-12-10T18:05:00Z",
    "completion_date"  :  "2024-12-11T15:30:00Z",
    "status": "Pending"        
}
8.	Send the Request
9.	Verify the Response 
For successful task creation, the response should include the message 
"Task is successfully created" with a 200 status code.
If there's any issue (ex: one of the validations isn’t satisfied.), the response should return appropriate error message





#####to test retrieve API
1.	Open Postman
2.	Select GET request type
3.	Enter endpoint url: http://127.0.0.1:5000/retrievetask
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	If you want to filter tasks based on status, start_date_range, or end_date_range, go to the Params tab and add the following parameters:
status: Pending
start_date_range: 2024-01-01T00:00:00
end_date_range: 2024-12-31T23:59:59
7.	Send the Request
8.	Verify the Response 
Retrieve tasks successfully (With or without filters), the response should return a list of tasks with a 200 status code (OK).
If no tasks are found or no tasks match the criteria, you should receive a 404 status code (Not Found) with a message: "No tasks found"



#### to test updatetask API
1.	Open Postman
2.	Select PUT request type
3.	Enter endpoint url: http://127.0.0.1:5000/updatetask/13 
*note:  we can replace 13 with the task we want to update  
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	Navigate to the Body tab then select raw data type and choose JSON format
7.	Enter JSON data in the body
{
    "title"  : "updated Task",
    "description"  : "updated TaskDescription",
    "start_date"  : " 2024-11-10T17:30:00Z",
    "due_date"  :  " 2024-11-10T18:05:00Z",
    "completion_date"  :  "2024-11-11T15:30:00Z",
    "status": "Pending"        
} # if any field not given will remain same as in database
8.	Send the Request
9.	Verify the Response 
If the task is updated successfully, you should receive a response with a 200 status code
If the task does not exist, you should receive a 404 status code
If there's any issue (ex: one of the validations isn’t satisfied.), the response should return appropriate error message




 #### to test deletetask API
1.	Open Postman
2.	Select DELETE request type
3.	Enter endpoint url: http://127.0.0.1:5000/deletetask/1
*note:  we can replace 1 with the task we want to delete  
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	Send the Request
7.	Verify the Response 
If the task is deleted successfully, you should receive a response with a 200 OK status code
If the task does not found, you should receive a 404 Not found status code




#### to test batchdeletetask API
1.	Open Postman
2.	Select DELETE request type
3.	Enter endpoint url: http://127.0.0.1:5000/batchdelete?start_datetime_range=2024-07-09T17:30:00Z&due_datetime_range=2024-07-21T17:30:00Z
*note:  we can change start and due date range.
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	Enter the Query Parameters: Go to the "Params" tab in Postman and add the query parameters for the start and due date-time ranges
7.	Send the Request
8.	Verify the Response 
If the batch is deleted successfully, you should receive a response with a 200 OK status code
If the task is not found, you should receive a 404 Not found status code
If invalid Date-Time Format given (400 Bad Request)

#### to test restoretask API
1.	Open Postman
2.	Select POST request type
3.	Enter endpoint url: http://127.0.0.1:5000/restoretasks
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	Send the Request
7.	Verify the Response 
- If tasks are found and successfully restored, there is a response message "# tasks restored successfully!" and status code will be 200 OK
- If no deleted tasks are found, there is a response message "No deleted tasks found to restore”




#####to test subscribe API
1.	Open Postman
2.	Select POST request type
3.	Enter endpoint url: http://127.0.0.1:5000/subscribe
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	Navigate to the Body tab then select raw data type and choose JSON format
7.	Enter JSON data in the body
{
    "start_date": "2024-12-10T16:05:00",
    "frequency": "daily",
    "report_time": 2
}
8.	Send the Request
9.	Verify the Response 
- If the subscription is created successfully, there is a response message and status code will be 200 OK
- If there's any issue (ex: one of the validations isn’t satisfied.), the response should return appropriate error message






#####to test unsubscribe API
1.	Open Postman
2.	Select DELETE request type
3.	Enter endpoint url: http://127.0.0.1:5000/unsubscribe
4.	Navigate to the Authorization tab and select the "Bearer Token" type
5.	Enter the Access Token in the "Token" field
6.	Send the Request
7.	Verify the Response 
- If the unsubscribe is created successfully, there is a response message and status code will be 200 OK
- If there's no subscription found, the response should return appropriate error message










