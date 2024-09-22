from flask import Flask, render_template, redirect, url_for, request, flash,jsonify
import os
from flask_pymongo import PyMongo # pip install Flask-pymongo
from bson import ObjectId
from datetime import datetime

# from forms import TaskForm

app = Flask(__name__, template_folder='templates')
app.config["MONGO_URI"] = "mongodb://localhost:27017/TaskManager"
db = PyMongo(app)
TaskManager = db.db 

# app.config['SECRET_KEY'] = 'your_secret_key'

# Route to List All Tasks (Read)
@app.route('/')
def index():
    # Check all tasks for overdue status
    check_overdue(db, createdTasks)

    # Retrieve all tasks from the database
    tasks = db.createdTasks.find()
    return render_template('index.html', tasks = tasks)

@app.route('/task')
def task():
    tasks = createdTasks.find()
    return render_template('task.html', tasks = tasks)

@app.route('/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        time = request.form['time']
        
        # Create a new task document
        task = {
            'title': title,
            'description': description,
            'date': date,
            'time': time,
            'completed': False
        }
        
        # Insert the task into the MongoDB database
        createdTasks.insert_one(task)
        print("Task created.")
        
        return redirect(url_for('index'))
    
    return render_template('task.html')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = db.createdTasks.find_one({"_id": ObjectId(task_id)})
    
    if task is None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Update the task with the submitted data
        createdTasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"title": request.form['title'], "description": request.form['description'], "date": request.form['date'], "time": request.form['time'], "status": request.form['status']}})

        # Check if the task should be marked as completed
        check_completed(db, createdTasks, task_id, request.form['status'])

        return redirect(url_for('index'))
    
    return render_template('edit.html', task=task)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    createdTasks.delete_one({"_id": ObjectId(task_id)})
    
    return redirect(url_for('index'))

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        event_name = request.form['event_name']
        description = request.form['description']
        date = request.form['date']
        time = request.form['time']
        status = request.form['status']

        # Create the event object and add it to the events list
        new_event = {
            'event_name' : event_name,
            'description' : description,
            'date' : date,
            'time' : time,
            'status' : status,
            'overdue' : False,
            'completed' : False
        }
        db.createdEvents.insert_one(new_event)
        check_completed(new_event)
        check_overdue(new_event)

        flash('Event created successfully!', 'success')
        return redirect(url_for('calendar'))
    
    return render_template('create_event.html')

@app.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    createdEvents.delete_one({"_id": ObjectId(event_id)})
    
    flash('Event deleted successfully!')
    return redirect(url_for('calendar'))

@app.route('/edit_event/<int:event_id>', methods=['GET'])
def edit_event(event_id):
    event_to_edit = createdEvents.find_one({"_id": ObjectId(event_id)})

    if event_to_edit is not None:
        return jsonify(event_to_edit), 200
    else:
        return jsonify({'error': 'Event not found!'}), 404

@app.route('/update_event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    data = request.get_json()
    updated = createdEvents.update_one({"_id": ObjectId(event_id)}, {"$set": {"event_name": data.get('event_name', ''), "description": data.get('description', ''), "date": data.get('date', ''), "time": data.get('time', '')}})
    check_completed(updated)
    check_overdue(updated)

    return jsonify({'message': 'Event updated successfully!'}), 200

def create_collections(TaskManager):
    """
    Creates collections in the TaskManager database.

    Args:
        TaskManager: The TaskManager object.

    Returns:
        None
    """
    collections = [
        {
            "name": "createdEvents",
            "validator": {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['event_name', 'description', 'status', 'date'],
                    'properties': {
                        'event_name': {"bsonType": "string"},
                        'description': {"bsonType": "string"},
                        'status': {"bsonType": "string"},
                        'date': {"bsonType": "date"},
                        'overdue': {"bsonType": "bool"},
                        'completed': {"bsonType": "bool"},
                    }
                }
            }
        },
        {
            "name": "deletedEvents",
            "validator": {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['event_name', 'description', 'status', 'date'],
                    'properties': {
                        'event_name': {"bsonType": "string"},
                        'description': {"bsonType": "string"},
                        'status': {"bsonType": "string"},
                        'date': {"bsonType": "date"},
                        'time': {"bsonType": "string"},
                        'overdue': {"bsonType": "bool"},
                        'completed': {"bsonType": "bool"},
                    }
                }
            }
        },
        {
            "name": "userCalendar",
            "validator": {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['background', 'dateToday'],
                    'properties': {
                        'background': {"bsonType": "string"},
                        'dateToday': {"bsonType": "date"}
                    }
                }
            }
        },
        {
            "name": "createdTasks",
            "validator": {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['event_name', 'description', 'status', 'date'],
                    'properties': {
                        'event_name': {"bsonType": "string"},
                        'description': {"bsonType": "string"},
                        'status': {"bsonType": "string"},
                        'date': {"bsonType": "date"},
                        'time': {"bsonType": "string"},
                        'overdue': {"bsonType": "bool"},
                        'completed': {"bsonType": "bool"},
                    }
                }
            }
        },
        {
            "name": "deletedTasks",
            "validator": {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['event_name', 'description', 'status', 'date'],
                    'properties': {
                        'event_name': {"bsonType": "string"},
                        'description': {"bsonType": "string"},
                        'status': {"bsonType": "string"},
                        'date': {"bsonType": "date"},
                        'time': {"bsonType": "string"},
                        'overdue': {"bsonType": "bool"},
                        'completed': {"bsonType": "bool"},
                    }
                }
            }
        }
    ]

    for collection in collections:
        TaskManager.create_collection(collection["name"], validator=collection["validator"])


# assign collections to respective variables
createdEvents = db.db["createdEvents"]
userCalendar = db.db["userCalendar"]
createdTasks = db.db["createdTasks"]


def check_overdue(event_id, task_id):
    def update_overdue(collection, id, due_date):
        today = datetime.date.today()
        collection.update_one({"_id": ObjectId(id)}, {"$set": {"overdue": due_date < today}})
    
    event = db.createdEvents.find_one({"_id": ObjectId(event_id)})
    if event:
        update_overdue(db.createdEvents, event_id, event["date"])
        print("Event is overdue.")
    
    task = db.createdSchedules.find_one({"_id": ObjectId(task_id)})
    if task:
        update_overdue(db.createdTasks, task_id, task["date"])
        print("Task is overdue.")

def check_completed(event_id, task_id):
    def update_completed(collection, id, status):
        collection.update_one({"_id" : ObjectId(id)}, {"$set" : {"status" : status == "completed"}})
    
    event = db.createdEvents.find_one({"_id": ObjectId(event_id)})
    if event:
        update_completed(db.createdEvents, event_id, event["status"])
        print("Event successfully marked as completed.")
    
    schedule = db.createdSchedules.find_one({"_id": ObjectId(task_id)})
    if schedule:
        update_completed(db.createdSchedules, task_id, task["status"])
        print("Task successfully marked as completed.")

# test code
# createdEvents.insert_one({"event_name": "Event 1", "description": "This is Event 1", "date": datetime(2024, 1, 1), "status": "in progress", "time": "10:00:00", "overdue" : False, "completed" : False})
# createdEvents.update_one({"event_name": "Event 1"}, { "$set" : {"description": "This is Event 1 Modified", "date": datetime(2024, 1, 1), "status": "completed", "time": "10:00:00"}})
# createdEvents.delete_one({"event_name": "Event 1"})

if __name__ == '__main__':
    app.run(debug=True)
