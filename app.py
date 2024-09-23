from flask import Flask, render_template, redirect, url_for, request, flash,jsonify
import os
from flask_pymongo import PyMongo # pip install Flask-pymongo
from bson import ObjectId
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.config["MONGO_URI"] = "mongodb://localhost:27017/TaskManager"
db = PyMongo(app)
TaskManager = db.db 


# Route to List All Tasks (Read)
@app.route('/')
def index():
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


def create_collections(TaskManager):
    collections = [
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


createdTasks = db.db["createdTasks"]



if __name__ == '__main__':
    app.run(debug=True)
