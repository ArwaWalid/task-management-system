from flask import Flask, request, jsonify
from db import db, bcrypt, jwt
from auth import auth_blueprint
from config import Config
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models import User, Tasks, Subscription
from datetime import datetime
from flask_mail import Mail, Message
from datetime import datetime, timedelta , timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
app = Flask(__name__)

# Load configuration before initializing extensions
app.config.from_object(Config)

# Initialize the extensions
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

# Register blueprints
app.register_blueprint(auth_blueprint)


#@app.route('/test', methods=['POST'])
#@jwt_required()
#def test():
 #   return jsonify(message="Authentication successful!"), 200



@app.route('/createtask', methods=['POST'])  # Create /createtask path for POST requests
@jwt_required()  # make sure if the user is authenticated before accessing this route
def createtask(): # fn that will be executed when a POST request is made (/createtask)
    data = request.get_json() #Extract data from the json request
    # Define allowed statuses
    allowed_statuses = ['Pending', 'Completed', 'Overdue']
    #extracting fields from the request
    title = data.get('title')
    description = data.get('description')
    # converting all dates from ISO string format to Python datetime objects
    # check that the dates in the request are in the valid format
    try:
        start_date = datetime.fromisoformat(data["start_date"].replace("Z", "+00:00"))
        due_date = datetime.fromisoformat(data["due_date"].replace("Z", "+00:00"))
        completion_date = datetime.fromisoformat(data["completion_date"].replace("Z", "+00:00"))
    except ValueError:
        return jsonify(message="Invalid date format. You have to enter date in ISO format."), 400 #status code 400 ~ bad request
    deleted_at = None
    status = data.get('status')
    # Validate status
    if status and status not in allowed_statuses:
        return jsonify(message=f"Invalid status. Allowed values are {', '.join(allowed_statuses)}."), 400 #status code 400 ~ bad request
    #validate start date is before due date
    if start_date >= due_date:
        return jsonify(message="Start date must be before due date."), 400  # status code 400 ~ bad request
    #validate start date is before completion date and completion date is before due date
    if completion_date < start_date:
        return jsonify(message="Start date must be before completion date."), 400  # 400 Bad Request
    if completion_date > due_date:
        return jsonify(message="Completion date be before due date."), 400  # 400 Bad Request
    # retrieve the user_id from the JWT token so the  task will be associated with the authenticated user who is creating it
    user_id = get_jwt_identity()
    #creating task object
    task = Tasks(user_id=user_id, title=title, description=description, deleted_at=deleted_at,start_date= start_date, due_date=due_date, completion_date=completion_date,status=status)
    db.session.add(task) # object can now be saved
    db.session.commit()  #save changes to database
    return jsonify(message="Task is successfully created"), 200 #status code 200 ~ OK



@app.route('/retrievetask', methods=['GET'])  # Create /retrievetask path for GET request
@jwt_required() # make sure if the user is authenticated before accessing this route
def retrievetask(): # fn that will be executed when a GET request is made (/retrievetask)
    status = request.args.get('status') # retrieve status filter for task
    start_date_range = request.args.get('start_date_range') # retrieve start date filter for task
    end_date_range = request.args.get('end_date_range') #retrieve end date filter for task
    user_id = get_jwt_identity()  #retrieve the user ID from JWT token for the user retrieving the task
    # Define allowed statuses
    allowed_statuses = ['Pending', 'Completed', 'Overdue']
    # Check if the provided status is valid
    if status and status not in allowed_statuses:
        return jsonify(message=f"Invalid status. Allowed values are {', '.join(allowed_statuses)}."), 400 # 400 Bad Request
    #filters tasks by the user_id and excludes tasks that have been deleted
    query = db.session.query(Tasks).filter(Tasks.user_id == user_id, None == Tasks.deleted_at)
    if status:
        query = query.filter(Tasks.status == status) #apply status filter if provided
    if start_date_range:
        start_date = datetime.fromisoformat(start_date_range)
        query = query.filter(Tasks.start_date >= start_date) # apply start date range filter if provided
    if end_date_range:
        end_date = datetime.fromisoformat(end_date_range)
        query = query.filter(Tasks.due_date <= end_date)  # apply end date range filter if provided
    tasks = query.all()   # excute the query to retrieve tasks
    if not tasks:     #no tasks found
        return jsonify(message="No tasks found"), 404 # 404 Not found
    # create an empty list to hold formatted task details for the response
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            "ID": task.id,
            "Title": task.title,
            "Description": task.description,
            "Start_date": task.start_date.isoformat(),
            "Due_date": task.due_date.isoformat(),
            "Completion_date": task.completion_date.isoformat() if task.completion_date else None,
            "Status": task.status
        })
    return jsonify(tasks=tasks_data), 200    # retrieve the tasks in the response #status code 200 ~ OK

@app.route('/updatetask/<int:task_id>', methods=['PUT'])  # Create /updatetask path for PUT request
@jwt_required()  # Make sure if the user is authenticated before accessing this route
def updatetask(task_id):
    data = request.get_json()  # Extract data from the JSON request
    user_id = get_jwt_identity()  # Retrieve the user ID from JWT token for the user updating the task
    # Filters tasks by the user_id and excludes tasks that have been deleted
    task = Tasks.query.filter_by(id=task_id, user_id=user_id, deleted_at=None).first()
    if not task:  # Task not found
        return jsonify(message="Task not found."), 404
    # Define allowed statuses
    allowed_statuses = ['Pending', 'Completed', 'Overdue']
    # Validate status
    status = data.get('status', task.status)
    if status and status not in allowed_statuses:
        return jsonify(message=f"Invalid status. Allowed values are {', '.join(allowed_statuses)}."), 400
    # Extract fields from the request
    title = data.get('title', task.title)
    description = data.get('description', task.description)
    start_date = data.get('start_date', task.start_date)
    due_date = data.get('due_date', task.due_date)
    completion_date = data.get('completion_date', task.completion_date)
    def make_timezone_aware(dt):
        if dt.tzinfo is None:  # Check if the datetime is naive
            return dt.replace(tzinfo=timezone.utc)  # Assume UTC for naive datetimes
        return dt
    def is_valid_iso_date(date_string):

        #Validates if the provided date string is in a valid ISO 8601 format.
        try:
            # Replace "Z" (common in ISO 8601) with "+00:00" for proper parsing
            datetime.fromisoformat(date_string.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False
    # Convert and validate start_date
    if isinstance(start_date, str):
        if not is_valid_iso_date(start_date):
            return jsonify(message="Invalid start date format. The date must be in ISO format."), 400
        start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    # Convert and validate due_date
    if isinstance(due_date, str):
        if not is_valid_iso_date(due_date):
            return jsonify(message="Invalid due date format. The date must be in ISO format."), 400
        due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
    # Convert and validate completion_date
    if isinstance(completion_date, str):
        if not is_valid_iso_date(completion_date):
            return jsonify(message="Invalid completion date format. The date must be in ISO format."), 400
        completion_date = datetime.fromisoformat(completion_date.replace("Z", "+00:00"))
    # Make all dates timezone-aware
    start_date = make_timezone_aware(start_date)
    due_date = make_timezone_aware(due_date)
    completion_date = make_timezone_aware(completion_date)
    #validate start date is before due date
    if start_date >= due_date:
        return jsonify(message="Start date must be earlier than due date."), 400
    #validate start date is before completion date and completion date is before due date
    if start_date >= completion_date:
        return jsonify(message="Start date must be earlier than completion date."), 400
    if completion_date >= due_date:
        return jsonify(message="Completion date must be earlier than due date."), 400
    # Update task attributes with the new values
    task.title = title
    task.description = description
    task.status = status
    task.start_date = start_date
    task.due_date = due_date
    task.completion_date = completion_date
    db.session.commit()
    return jsonify(message="Task updated successfully!!"), 200  # Status code 200 ~ OK



@app.route('/deletetask/<int:task_id>', methods=['DELETE']) # Create /createtask path for DELETE requests
@jwt_required() # Make sure if the user is authenticated before accessing this route
def deletetask(task_id):
    user_id = get_jwt_identity()   # Retrieve the user ID from JWT token for the user updating the task
    # Filters tasks by the user_id and excludes tasks that have been deleted
    task = Tasks.query.filter_by(id=task_id, user_id=user_id, deleted_at=None).first()
    if not task:
        return jsonify(message="Task not found."), 404 #status 404 ~ Not found
    # Mark the task as deleted
    task.deleted_at = datetime.utcnow()  # Set deleted_at to current time
    db.session.commit()
    return jsonify(message="Task deleted successfully!"), 200


@app.route('/batchdelete', methods=['DELETE'])  # Create /batchdelete path for DELETE requests
@jwt_required()
def batch_delete():
    # Get the date-time range from query parameters
    start_datetime_range = request.args.get('start_datetime_range')
    due_datetime_range = request.args.get('due_datetime_range')
    if not start_datetime_range or not due_datetime_range:
        return jsonify(message="Both start_datetime_range and due_datetime_range are required."), 400 #not in time range
    try:
        # Convert string to datetime objects
        start_datetime = datetime.strptime(start_datetime_range, "%Y-%m-%d %H:%M:%S")
        due_datetime = datetime.strptime(due_datetime_range, "%Y-%m-%d %H:%M:%S")
        user_id = get_jwt_identity()
        # Find tasks in time range
        tasks_to_delete = db.session.query(Tasks).filter(
            Tasks.user_id == user_id,
            Tasks.deleted_at == None,
            Tasks.start_date > start_datetime,
            Tasks.due_date < due_datetime
        ).all()
        if not tasks_to_delete:
            return jsonify(message="No tasks found for the given period."), 404 #not found
        for task in tasks_to_delete:
            task.deleted_at = datetime.utcnow() # Delete tasks
        db.session.commit()
        return jsonify(message=f"{len(tasks_to_delete)} tasks deleted successfully!"), 200
    except ValueError:
        return jsonify(message="Invalid date-time format. Please use YYYY-MM-DD HH:MM:SS."), 400 #invalid format


@app.route('/restoretasks', methods=['POST'])
@jwt_required()
def restore_last_deleted_tasks():
    user_id = get_jwt_identity()
    # Find tasks that have been deleted, ordered by the most recent deleted
    last_deleted_tasks = db.session.query(Tasks).filter(
        Tasks.user_id == user_id,
        Tasks.deleted_at != None  #tasks are deleted
    ).order_by(Tasks.deleted_at.desc()).all()
    # ensure there is deleted tasks
    if not last_deleted_tasks:
        return jsonify(message="No deleted tasks found to restore."), 404
    # Get the most recent deleted time
    last_deleted_at = last_deleted_tasks[0].deleted_at
    #if any other task deleted at the same time restore it
    tasks_to_restore = db.session.query(Tasks).filter(
        Tasks.user_id == user_id,
        Tasks.deleted_at == last_deleted_at
    ).all()
    # Restore the tasks (set the deleted_at value to null)
    for task in tasks_to_restore:
        task.deleted_at = None
    db.session.commit()
    return jsonify(message=f"{len(tasks_to_restore)} tasks restored successfully!"), 200



#extract data -> validate input -> check if user already subscribed  -> create new subs -> Respond

# Allowed frequencies
ALLOWED_FREQUENCIES = ['daily', 'weekly', 'monthly']
@app.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    user_id = get_jwt_identity()
    data = request.get_json()
    start_date = data.get('start_date')
    frequency = data.get('frequency')
    report_time = data.get('report_time')
    try:
    # Validate start_date in the correct format
        start_date = datetime.fromisoformat(start_date.replace("Z","+00:00"))
    except (ValueError, TypeError):
        return jsonify(message="Invalid start_date format."), 400
    # Validate frequency
    if frequency not in ALLOWED_FREQUENCIES:
        return jsonify(message=f"Invalid frequency. Allowed values are: {', '.join(ALLOWED_FREQUENCIES)}"), 400
    # Validate report_time
    try:
        report_time = int(report_time)
        if not (0 <= report_time <= 23): # 0->23 hr
            return jsonify(
                message="Invalid report_time. It should be a valid hour (0-23) with no minutes or seconds."), 400
    except (ValueError, TypeError):
        return jsonify(message="Invalid report_time. It should be a valid hour (0-23) with no minutes or seconds."), 400
    # Check if the user already has a subscription
    existing_subscription = Subscription.query.filter_by(user_id=user_id).first()
    if existing_subscription:
        return jsonify(message="User already has another subsc..."), 400
        # Check if the user has at least one task
    existing_tasks = Tasks.query.filter_by(user_id=user_id).all()
    if not existing_tasks:
        # If no tasks are found, the subscription will start after the first task is created
        return jsonify(message="User can only subscribe if he has at least one task."), 400
    # new subscription
    new_subscription = Subscription(
        user_id=user_id,
        start_date=start_date,
        frequency=frequency,
        report_time=report_time,
        next_send_time= start_date
    )
    # Add the subscription to the database and commit
    db.session.add(new_subscription)
    db.session.commit()
    return jsonify(message="Subscription created successfully!"), 200




@app.route('/unsubscribe', methods=['DELETE'])
@jwt_required()
def unsubscribe():
    user_id = get_jwt_identity()
    #data = request.get_json()
    subscription = Subscription.query.filter_by(user_id=user_id).first()
    if not subscription:
        return jsonify(message="No active subscription found for this user."), 404
    db.session.delete(subscription)
    db.session.commit()
    return jsonify(message="Subscription deleted successfully!"), 200




# Mail Config (tools needed to send email)
# Setup the sending email using flask mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com', #address of email (gmail)
    MAIL_PORT=587, #The port used for sending email
    MAIL_USE_TLS=True, #make email connection safe
    MAIL_USERNAME='vodafonetaskreports@gmail.com',  #FOR AUTHENTICATION
    MAIL_PASSWORD='cspj tkab dsie xjgk' #special app password
    #to get this unique password
    #Enable 2-Step Verification in your Gmail account.
    #Go to Security Settings → App Passwords in Gmail.
    #Select the app and device, then Gmail generates a unique password
)
mail = Mail(app) #Connects Flask-Mail to the project.
def generate_report():
    with app.app_context(): #ensures the Flask app has access to Database and Email
        users = User.query.all() #get all users from database
        #check if user have a subscription and extract subscription details
        for user in users:
            if user.subscription:
                user_id = user.id
                frequency = user.subscription.frequency
                report_time = user.subscription.report_time
                next_send_time = user.subscription.next_send_time
                now = datetime.utcnow() #utc -2 hours from cairo
                if next_send_time > now:
                    print("hi")
                    return   #HANFDL FE AL LOOP DE LEHAD MA AL NEXT SEND TIME< NOW WE NAKAML BA2E AL CODE
               #FREQUENCY VALIDATION
                if frequency == 'daily':
                    time_limit = now - timedelta(days=1) #AKHER 24 HR
                    next_send_time = next_send_time +timedelta(days=1)  #AL ADEM + 24 HR 3ASHAN YATB3T ONCE DIALY
                elif frequency == 'weekly':
                    time_limit = now - timedelta(weeks=1) #AKHER 24*7 HR
                    next_send_time = next_send_time + timedelta(weeks=1)
                elif frequency == 'monthly':
                    time_limit = now - timedelta(days=30) #AKHER 24*30 HR
                    next_send_time = next_send_time + timedelta(days=30) #timedelta class doesn't support months
                else:
                    return None  # Invalid frequency
                user.subscription.next_send_time = next_send_time #UPDATE AL NEXT SEND TIME 3AND AL USER
                db.session.commit() #APPLY CHANGES
                if report_time == now.hour:     # Check if it is time to send the email
                    # query user tasks within al range
                    tasks = Tasks.query.filter(
                        Tasks.user_id == user_id,
                        Tasks.due_date >= time_limit,
                        Tasks.deleted_at.is_(None) #l2no msh hy-retrieve l deleted tasks
                    ).all()
                    task_data = {
                        "Pending": [],
                        "Completed": [],
                        "Overdue": []
                    }
                #invoke email
                    for task in tasks:
                        if task.status == "Pending":
                            task_data["Pending"].append(task)
                        elif task.status == "Completed":
                            task_data["Completed"].append(task)
                        elif task.status == "Overdue":
                            task_data["Overdue"].append(task)
                    #HTML EMAIL
                    html_content = """
                    <html>
                        <body>
                            <h1>Task Report</h1>
                
                            <h2>Pending Tasks</h2>
                            <table border="1" style="border-collapse: collapse; width: 100%;">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Due Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                    """
                    for task in task_data["Pending"]:
                        html_content += f"""
                                    <tr>
                                        <td>{task.title}</td>
                                        <td>{task.due_date}</td>
                                    </tr>
                        """
                    html_content += """
                                </tbody>
                            </table>
                
                            <h2>Completed Tasks</h2>
                            <table border="1" style="border-collapse: collapse; width: 100%;">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Completion Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                    """
                    for task in task_data["Completed"]:
                        html_content += f"""
                                    <tr>
                                        <td>{task.title}</td>
                                        <td>{task.completion_date}</td>
                                    </tr>
                        """
                    html_content += """
                                </tbody>
                            </table>
                
                            <h2>Overdue Tasks</h2>
                            <table border="1" style="border-collapse: collapse; width: 100%;">
                                <thead>
                                    <tr>
                                        <th>Title</th>
                                        <th>Due Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                    """
                    for task in task_data["Overdue"]:
                        html_content += f"""
                                    <tr>
                                        <td>{task.title}</td>
                                        <td>{task.due_date}</td>
                                    </tr>
                        """
                    html_content += """
                                </tbody>
                            </table>
                        </body>
                    </html>
                    """
                    # Send email
                    msg = Message(
                        subject="Your Task Report",
                        sender="vodafonetaskreports@gmail.com",  #SENDER EMAIL
                        recipients=["arwawalid2882001@gmail.com",
                                    user.email], #user email
                                                 #arwawalid2882001@gmail.com ONLY FOR TRIAL
                        html=html_content
                    )
                    mail.send(msg)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.start()
# Schedule the task to run every 1 MINUTE
#we can make the task better to run every 1 hour by making the interval run every 60 min
# at the case of running each one hr i have to run the server exactly at the start of the hour ex : 9:00
scheduler.add_job(func=generate_report, trigger=IntervalTrigger(minutes=1), id='email_task', replace_existing=True)

# make scheduler starts when the app receives a request,if it isn't already running.
@app.before_request
def init_scheduler():
    if not scheduler.running:
        scheduler.start()




if __name__ == "__main__":
    app.run(debug=True)
