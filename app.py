from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request,flash,jsonify
import os

# from forms import TaskForm

app = Flask(__name__, template_folder='templates')
# app.config['SECRET_KEY'] = 'your_secret_key'

# In-memory task list to simulate a database - to be changed to database 
tasks = []

# Route to List All Tasks (Read)
task_list = []

#function to get the event for that specific date
def get_events_for_date(date):
    for task in tasks:
        if str(task['date']) == str(date):
            task_list.append(task)
    return task_list


@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)


#Route direct to tasks page
@app.route('/task')
def task():
    return render_template('task.html', tasks=tasks)


# Create route 
@app.route('/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date = request.form['date']  # Get date input
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        # Store date and time separately
        new_task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description,
            'date': date,  # Store the date
            'time': start_time + ' - ' + end_time,  # Store the time
            'completed': False
        }
        tasks.append(new_task)
        
        return redirect(url_for('index'))
    
    return render_template('task.html')

#update route 
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    
    if task is None:  # Check if task was found
        return redirect(url_for('index'))  # Redirect to the task list or index page

    if request.method == 'POST':
        # Update the task with the submitted data
        task['title'] = request.form['title']
        task['description'] = request.form['description']
        task['date'] = request.form['date']
        task['time'] = request.form['start_time'] + ' - ' + request.form['end_time']

        return redirect(url_for('index'))  # Redirect to the task list after editing
    
    return render_template('edit.html', task=task)  # Render edit template if task is found


#Delete route 
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    global tasks  # Make sure to reference the global tasks list
    # Find the task by its ID
    task_to_delete = next((task for task in tasks if task['id'] == task_id), None)
    
    if task_to_delete:
        tasks.remove(task_to_delete)  # Remove the task from the list
        task_list.remove(task_to_delete)
    else:
        flash('Task not found!', 'error')
    
    return redirect(url_for('index'))  # Redirect back to the task list

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/events', methods=['GET'])
def get_events():
    day = int(request.args.get('day'))
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))

    # Create a date object and format it with leading zeros
    selected_date = datetime(year, month, day)
    formatted_date = selected_date.strftime('%Y-%m-%d')

    events = get_events_for_date(formatted_date)  # Assume this function fetches events from DB

    if events:
        return jsonify({'events': events})
    else:
        return jsonify({'events': []}), 200  # Return empty list if no events


# Route to Add Event (Create) in calendar
# @app.route('/create_event', methods=['GET', 'POST'])
# def create_event():
#     if request.method == 'POST':
#         event_name = request.form['eventname']
#         start_time = request.form['start_time']
#         end_time = request.form['end_time']
#         description = request.form['description']
#         event_date = request.form['event_date']
#         # Create the event object and add it to the events list
#         new_event = {
#             'id': len(events) + 1,
#             'eventname': event_name,
#             'description': description,
#             'date': event_date,  # Store the date
#             'time': start_time + '-' + end_time,  # Store the time
#         }
#         events.append(new_event)  # Append the new event to the list
#
#         return redirect(url_for('calendar'))  # Redirect to calendar after creating the event
#
#     return render_template('calendar.html',events=events)




# Route to Delete Event (Optional)in calendar
# @app.route('/delete_event/<int:event_id>', methods=['POST'])
# def delete_event(event_id):
#     global events
#     # Find the event by its ID
#     event_to_delete = next((event for event in events if event['id'] == event_id), None)
#
#     if event_to_delete:
#         events.remove(event_to_delete)  # Remove the event from the list
#         flash('Event deleted successfully!', 'success')
#     else:
#         flash('Event not found!', 'error')
#
#     return redirect(url_for('calendar'))  # Redirect back to the calendar
#
# #Route to edit the event
# @app.route('/edit_event/<int:event_id>', methods=['GET'])
# def edit_event(event_id):
#     # Attempt to find the event by its ID
#     event_to_edit = next((event for event in events if event['id'] == event_id), None)
#
#     # Check if the event exists
#     if event_to_edit is not None:
#         return jsonify(event_to_edit), 200  # Return the event details as JSON with 200 status
#     else:
#         # Return a structured error message if the event is not found
#         return jsonify({'error': 'Event not found!'}), 404
#
#
# #update request
# @app.route('/update_event/<int:event_id>', methods=['POST'])
# def update_event(event_id):
#     data = request.get_json()
#     event_to_update = next((event for event in events if event['id'] == event_id), None)
#
#     if event_to_update:
#         # Update the event details
#         event_to_update['title'] = data.get('title', event_to_update['title'])
#         event_to_update['time'] = data.get('time', event_to_update['time'])
#         event_to_update['description'] = data.get('description', event_to_update['description'])
#         event_to_update['date'] = data.get('date', event_to_update['date'])
#
#         return jsonify({'message': 'Event updated successfully!', 'event': event_to_update}), 200
#     else:
#         return jsonify({'error': 'Event not found!'}), 404
#


if __name__ == '__main__':
    app.run(debug=True)
