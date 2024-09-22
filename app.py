from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request,flash,jsonify

app = Flask(__name__, template_folder='templates')

# In-memory task list to simulate a database - to be changed to database 
tasks = []

# Dictionary to store tasks by date
tasks_by_date = {}


# Function to get the events for that specific date
def get_task_by_date(date):
    return tasks_by_date.get(date, [])

#Route to direct to index page 
@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)


#Route direct to tasks page
@app.route('/task')
def task():
    return render_template('task.html', tasks=tasks)


# Create route - task form 
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
            'date': date,  
            'time': start_time + ' - ' + end_time,  # Store time range (start & end)
            'completed': False
        }
        tasks.append(new_task)
        
          # task grouped by date
        if date not in tasks_by_date:
            tasks_by_date[date] = []
        tasks_by_date[date].append(new_task)
      
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
    else:
        flash('Task not found!', 'error')
    
    return redirect(url_for('index'))  # Redirect back to the task list

#Calendar page to get events by date 
@app.route('/calendar')
def calendar():
    return render_template('calendar.html', get_task_by_date = get_task_by_date)

@app.route('/events', methods=['GET'])
def get_events():
    day = int(request.args.get('day'))
    month = int(request.args.get('month'))
    year = int(request.args.get('year'))

    # Create a date object and format it with leading zeros
    selected_date = datetime(year, month, day)
    formatted_date = selected_date.strftime('%Y-%m-%d')

    events = get_task_by_date(formatted_date)  #function to fetch from db 

    if events:
        return jsonify({'events': events})
    else:
        return jsonify({'events': []}), 200  # Return empty list if no events


if __name__ == '__main__':
    app.run(debug=True)
