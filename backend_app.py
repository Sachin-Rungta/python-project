from flask import Flask, request, jsonify, make_response
import sqlite3
from time import time
from datetime import datetime as dt
from enum import Enum

app = Flask(__name__)

# Create a database connection and create the task table if it doesn't exist
conn = sqlite3.connect('tasks.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            eta TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# User Story 0 - Check App status
@app.route('/', methods=['GET'])
def home():
    return "app is active"

# User Story 1 - Create Task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    # Parse request data
    title = request.json.get('title')
    eta = request.json.get('eta') or dt.date.today()+dt.timedelta(weeks=1)
    status = request.json.get('status') or 'Pending'
    if status not in ["Pending", "In Progress", "Complete", "In Review"]:
        return make_response(jsonify({'message': 'invalid status'}), 404) 

    # Insert task into database
    c.execute("INSERT INTO tasks (title, eta, status) VALUES (?, ?, ?)", (title, eta, status))
    conn.commit()

    # Return created task
    c.execute("SELECT * FROM tasks WHERE id=?", (c.lastrowid,))
    task = c.fetchone()
    return make_response(jsonify(task), 201)

# User Story 2 - Retrieve Task
@app.route('/api/tasks/<int:id>', methods=['GET'])
def get_task(id):
    # Retrieve task from database
    c.execute("SELECT title, eta, status FROM tasks WHERE id=?", (id,))
    task = c.fetchone()

    # Return task or 404 if not found
    if task:
        return make_response(jsonify(task), 200)
    else:
        return make_response(jsonify({'message': 'Task not found'}), 404)

# User Story 3 - Retrieve All Tasks
@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    # Retrieve all tasks from database
    c.execute("SELECT id, title, eta, status FROM tasks")
    tasks = c.fetchall()

    # Return tasks
    return make_response(jsonify(tasks), 200)

# User Story 4 - Update Task
@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    # Parse request data
    title = request.json.get('title')
    eta = request.json.get('eta')
    status = request.json.get('status')
    if status not in ["Pending", "In Progress", "Complete", "In Review"]:
        return make_response(jsonify({'message': 'invalid status'}), 404) 

    # Retrieve current task from database
    c.execute("SELECT * FROM tasks WHERE id=?", (id,))
    current_task = c.fetchone()

    # Update task in database
    if title:
        c.execute("UPDATE tasks SET title=?, updated_at=? WHERE id=?", (title, dt.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    if eta:
        c.execute("UPDATE tasks SET eta=?, updated_at=? WHERE id=?", (eta, dt.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    if status:
        c.execute("UPDATE tasks SET status=?, updated_at=? WHERE id=?", (status, dt.now().strftime("%Y-%m-%d %H:%M:%S"), id))
    conn.commit()

    # Retrieve updated task from database
    c.execute("SELECT * FROM tasks WHERE id=?", (id,))
    updated_task = c.fetchone()

    # Return updated task or 404 if not found
    if updated_task:
        return make_response(jsonify(updated_task),200)
    else:
        return make_response(jsonify({'message': 'Task not found'}), 404)

# User Story 5 - Audit Task
@app.route('/api/tasks/audit/<int:id>', methods=['GET'])
def audit_task(id):
    # Retrieve current task from database
    c.execute("SELECT * FROM tasks WHERE id=? AND created_at != updated_at", (id,))
    updated_task = c.fetchone()

    # Return updated task or 404 if not found
    if updated_task:
        return make_response(jsonify(updated_task),200)
    else:
        return make_response(jsonify({'message': 'Task not found'}), 404)

@app.route('/api/tasks/delete/<int:id>', methods=['POST'])
def delete_task(id):
    # Retrieve task from database
    c.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = c.fetchone()
    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    # Delete task
    c.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200

    
if __name__ == '__main__':
    app.run(debug=True)