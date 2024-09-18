from flask import Flask, render_template, redirect, url_for, request, flash
import os

# from forms import TaskForm

app = Flask(__name__, template_folder='../frontend')
# app.config['SECRET_KEY'] = 'your_secret_key'

# In-memory task list to simulate a database - to be changed to database 
tasks = []

# Route to List All Tasks (Read)
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
        time = request.form['time']  # Get time input
        
        # Store date and time separately
        new_task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': description,
            'date': date,  # Store the date
            'time': time,  # Store the time
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
        task['time'] = request.form['time']
        
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




if __name__ == '__main__':
    app.run(debug=True)
