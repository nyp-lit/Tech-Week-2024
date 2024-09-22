from flask import Flask, render_template, redirect, url_for, request, flash,jsonify
import os
from collections import defaultdict  # Importing defaultdict
from flask_pymongo import PyMongo # pip install Flask-pymongo
from bson import ObjectId
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.config["MONGO_URI"] = "mongodb://localhost:27017/TaskManager"
db = PyMongo(app)
TaskManager = db.db 

# app.config['SECRET_KEY'] = 'your_secret_key'

# Route to List All Tasks (Read)
@app.route('/')
def index():
    # Check all tasks for overdue status
    # check_overdue(db, createdTasks)

    # Retrieve all tasks from the database
    tasks = createdTasks.find()
    return render_template('index.html', tasks=tasks)


@app.route('/task')
def task():
    tasks = createdTasks.find()
    return render_template('task.html', tasks=tasks)


#Create task route 
@app.route('/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        
        # Convert the date string to a datetime object
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')  # Convert 'YYYY-MM-DD' string to date object
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
        
        # Create a new task document
        task = {
            'title': title,
            'description': description,
            'date': date_obj,  # Use the converted datetime object here
            'time': start_time + ' - ' + end_time,
            'completed': False
        }

        # Insert the task into the MongoDB database
        createdTasks.insert_one(task)
        print("Task created.")
        
        return redirect(url_for('index'))
    
         # Fetch all tasks to display in the "Edit" section
    tasks = list(createdTasks.find())
    
    return render_template('task.html', tasks=tasks)

#edit 
@app.route('/edit/<string:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = createdTasks.find_one({"_id": ObjectId(task_id)})
    
    if task is None:
        flash("Task not found.", "warning")
        return redirect(url_for('index'))

    if request.method == 'POST':
        updated_fields = {}

        if 'title' in request.form and request.form['title']:
            updated_fields['title'] = request.form['title']
        if 'description' in request.form and request.form['description']:
            updated_fields['description'] = request.form['description']
        
        if 'date' in request.form and request.form['date']:
            try:
                date_obj = datetime.strptime(request.form['date'], '%Y-%m-%d')
                updated_fields['date'] = date_obj
            except ValueError:
                return render_template('edit_task.html', task=task, error_message="Invalid date format. Please use YYYY-MM-DD.")
        
        if 'start_time' in request.form and request.form['start_time']:
            if 'end_time' in request.form and request.form['end_time']:
                updated_fields['time'] = f"{request.form['start_time']} - {request.form['end_time']}"

        print("Updated fields:", updated_fields)  # Debugging line

        if updated_fields:
            try:
                result = createdTasks.update_one({"_id": ObjectId(task_id)}, {"$set": updated_fields})
                if result.matched_count > 0:
                    return redirect(url_for('index'))
                else:
                    flash("No changes were made to the task.", "info")
            except Exception as e:
                flash(f"An error occurred while updating: {str(e)}", "danger")
        
        else:
            return render_template('edit_task.html', task=task)
    
    return render_template('edit_task.html', task=task)


#Delete route 
@app.route('/delete/<string:task_id>', methods=['POST'])
def delete_task(task_id):
    createdTasks.delete_one({"_id": ObjectId(task_id)})
    
    return redirect(url_for('index'))

#calendar

@app.route('/events', methods=['GET'])
def get_events_by_date():
    # Extract query parameters for day, month, and year
    day = request.args.get('day')
    month = request.args.get('month')
    year = request.args.get('year')

    # Format the date string as 'YYYY-MM-DD'
    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Convert the date string to a datetime object for MongoDB query
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

    # Query MongoDB for tasks matching this date
    tasks = createdTasks.find({"date": date_obj})

    # Convert the results to a list and convert ObjectId to a string
    task_list = []
    for task in tasks:
        task['_id'] = str(task['_id'])
        task_list.append(task)

    # Return the tasks as JSON
    return jsonify({"events": task_list})

@app.route('/calendar')
def calendar():
    # Fetch all tasks and sort them by date
    tasks = createdTasks.find().sort("date")  # Sorting by date

    # Convert cursor to a list and convert ObjectId to string
    tasklist = []
    for task in tasks:
        task['_id'] = str(task['_id'])  # Convert ObjectId to string
        tasklist.append(task)

    return render_template('calendar.html', tasks=tasklist)



# @app.route('/create_event', methods=['GET', 'POST'])
# def create_event():
#     if request.method == 'POST':
#         event_name = request.form['event_name']
#         description = request.form['description']
#         date = request.form['date']
#         time = request.form['time']
#         status = request.form['status']

#         # Create the event object and add it to the events list
#         new_event = {
#             'event_name' : event_name,
#             'description' : description,
#             'date' : date,
#             'time' : time,
#             'status' : status,
#             'overdue' : False,
#             'completed' : False
#         }
#         createdEvents.insert_one(new_event)
#         check_completed(new_event)
#         check_overdue(new_event)

#         flash('Event created successfully!', 'success')
#         return redirect(url_for('calendar'))
    
#     return render_template('create_event.html')

# @app.route('/delete_event/<int:event_id>', methods=['POST'])
# def delete_event(event_id):
#     createdEvents.delete_one({"_id": ObjectId(event_id)})
    
#     flash('Event deleted successfully!')
#     return redirect(url_for('calendar'))

# @app.route('/edit_event/<int:event_id>', methods=['GET'])
# def edit_event(event_id):
#     event_to_edit = createdEvents.find_one({"_id": ObjectId(event_id)})

#     if event_to_edit is not None:
#         return jsonify(event_to_edit), 200
#     else:
#         return jsonify({'error': 'Event not found!'}), 404

# @app.route('/update_event/<int:event_id>', methods=['POST'])
# def update_event(event_id):
#     data = request.get_json()
#     updated = createdEvents.update_one({"_id": ObjectId(event_id)}, {"$set": {"event_name": data.get('event_name', ''), "description": data.get('description', ''), "date": data.get('date', ''), "time": data.get('time', '')}})
#     check_completed(updated)
#     check_overdue(updated)

#     return jsonify({'message': 'Event updated successfully!'}), 200

def create_collections(TaskManager):
    collections = [
        # {
        #     "name": "createdEvents",
        #     "validator": {
        #         '$jsonSchema': {
        #             'bsonType': 'object',
        #             'required': ['event_name', 'description', 'status', 'date'],
        #             'properties': {
        #                 'event_name': {"bsonType": "string"},
        #                 'description': {"bsonType": "string"},
        #                 'status': {"bsonType": "string"},
        #                 'date': {"bsonType": "date"},
        #                 'overdue': {"bsonType": "bool"},
        #                 'completed': {"bsonType": "bool"},
        #             }
        #         }
        #     }
        # },
        # {
        #     "name": "deletedEvents",
        #     "validator": {
        #         '$jsonSchema': {
        #             'bsonType': 'object',
        #             'required': ['event_name', 'description', 'status', 'date'],
        #             'properties': {
        #                 'event_name': {"bsonType": "string"},
        #                 'description': {"bsonType": "string"},
        #                 'status': {"bsonType": "string"},
        #                 'date': {"bsonType": "date"},
        #                 'time': {"bsonType": "string"},
        #                 'overdue': {"bsonType": "bool"},
        #                 'completed': {"bsonType": "bool"},
        #             }
        #         }
        #     }
        # },
    #    {
    #         "name": "userCalendar",
    #         "validator": {
    #             '$jsonSchema': {
    #                 'bsonType': 'object',
    #                 'required': ['background', 'dateToday'],
    #                 'properties': {
    #                     'background': {"bsonType": "string"},
    #                     'dateToday': {"bsonType": "date"}
    #                 }
    #             }
    #         }
    #     },
        {
            "name": "createdTasks",
            "validator": {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['title', 'description', 'date'],
                    'properties': {
                        'title': {"bsonType": "string"},
                        'description': {"bsonType": "string"},
                        'date': {"bsonType": "date"},
                        'time': {"bsonType": "string"},
                        # 'overdue': {"bsonType": "bool"},
                        # 'completed': {"bsonType": "bool"},
                    }
                }
            }
        },
        {
            "name": "deletedTasks",
            "validator": {
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['title', 'description', 'date'],
                    'properties': {
                        'title': {"bsonType": "string"},
                        'description': {"bsonType": "string"},
                        # 'status': {"bsonType": "string"},
                        'date': {"bsonType": "date"},
                        'start_time': {"bsonType": "string"},
                        'end_time': {"bsonType": "string"},
                        'overdue': {"bsonType": "bool"},
                        'completed': {"bsonType": "bool"},
                    }
                }
            }
        },
        {
    "name": "updatedTasks",
    "validator": {
        '$jsonSchema': {
            'bsonType': 'object',
            'properties': {
                'title': {"bsonType": "string"},  # Title of the task
                'description': {"bsonType": "string"},  # Description of the task
                'date': {"bsonType": "date"},           # Date of the task
                'time': {"bsonType": "string"},         # Time range for the task (e.g., "09:00 - 10:00")
                'start_time': {"bsonType": "string"},   # Start time
                'end_time': {"bsonType": "string"},     # End time
                'overdue': {"bsonType": "bool"},        # Overdue status
                'completed': {"bsonType": "bool"},      # Completion status
            }
        }
    }
}

    ]

    existing_collections = TaskManager.list_collection_names()

    for collection in collections:
        if collection["name"] not in existing_collections:
            TaskManager.create_collection(collection["name"], validator=collection["validator"])

# Create collections when the app starts
create_collections(TaskManager)

# assign collections to respective variables
# createdEvents = db.db["createdEvents"]
# userCalendar = db.db["userCalendar"]
createdTasks = db.db["createdTasks"]

#To be checked 
# def check_overdue(event_id, task_id):
#     def update_overdue(collection, id, due_date):
#         today = datetime.date.today()
#         collection.update_one({"_id": ObjectId(id)}, {"$set": {"overdue": due_date < today}})
    
#     event = createdEvents.find_one({"_id": ObjectId(event_id)})
#     if event:
#         update_overdue(createdEvents, event_id, event["date"])
#         print("Event is overdue.")
    
#     task = createdTasks.find_one({"_id": ObjectId(task_id)})
#     if task:
#         update_overdue(createdTasks, task_id, task["date"])
#         print("Task is overdue.")

#To be checked 
# def check_completed(event_id, task_id):
#     def update_completed(collection, id, status):
#         collection.update_one({"_id" : ObjectId(id)}, {"$set" : {"status" : status == "completed"}})
    
#     event = createdEvents.find_one({"_id": ObjectId(event_id)})
#     if event:
#         update_completed(createdEvents, event_id, event["status"])
#         print("Event successfully marked as completed.")
    
#     task = createdTasks.find_one({"_id": ObjectId(task_id)})
#     if task:
#         update_completed(createdTasks, task_id, task["status"])
#         print("Task successfully marked as completed.")

# test code
# createdEvents.insert_one({"event_name": "Event 1", "description": "This is Event 1", "date": datetime(2024, 1, 1), "status": "in progress", "time": "10:00:00", "overdue" : False, "completed" : False})
# createdEvents.update_one({"event_name": "Event 1"}, { "$set" : {"description": "This is Event 1 Modified", "date": datetime(2024, 1, 1), "status": "completed", "time": "10:00:00"}})
# createdEvents.delete_one({"event_name": "Event 1"})

if __name__ == '__main__':
    app.run(debug=True)
