from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid  # To generate unique IDs

app = Flask(__name__, template_folder='templates')

todos = []

@app.route('/')
def index():
    return render_template('index.html', todos=todos)

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.get_json()
    todos.append({'id': str(uuid.uuid4()), 'name': task['name'], 'date': task['date']})
    return jsonify({'success': True})

@app.route('/delete_task/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global todos
    todos = [task for task in todos if task['id'] != task_id]
    return jsonify({'success': True})

@app.route('/edit_task/<string:task_id>', methods=['POST'])
def edit_task(task_id):
    task_data = request.get_json()
    for task in todos:
        if task['id'] == task_id:
            task['name'] = task_data['name']
            task['date'] = task_data['date']
            break
    return jsonify({'success': True})

@app.route('/tasks')
def get_tasks():
    return jsonify(todos)

if __name__ == '__main__':
    app.run(debug=True)