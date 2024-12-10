#defines database models
from db import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    hidden = db.Column(db.Boolean, nullable=False, default=False)
    subscription = db.relationship('Subscription', backref='user', uselist=False)  # One-to-One relationship

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)

    description = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    completion_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(120), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    frequency = db.Column(db.String(120), nullable=False)
    report_time = db.Column(db.Integer, nullable=False)
    next_send_time = db.Column(db.DateTime, nullable=False)   #AL MARA AL GAYA AL HAYTB3T AL REPORT FEHA


class Email_Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=False)
    report_date = db.Column(db.DateTime, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)


    def __repr__(self):
        return f'<User {self.username}>'
