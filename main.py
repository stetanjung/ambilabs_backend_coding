from flask import Flask, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, asc
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///tasks_ambilabs.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
tz = pytz.timezone('Asia/Hong_Kong')

db = SQLAlchemy(app)

class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String)
    expired = db.Column(db.DateTime(timezone=True), nullable=False)
    
    def __init__(self, task_id, title, description, expired):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.expired = expired

db.create_all()


# fetch all the tasks with all the past tasks
@app.route("/tasks/all", methods=['GET'])
def get_all_tasks():
    tasks = []
    # query the tasks from db order ascending by the tasks' expired
    query_tasks = Tasks.query.order_by(asc(Tasks.expired)).all()
    
    # if tasks not found return empty list
    if query_tasks == None:
        return jsonify({
            "result": tasks
        }), 200
    
    for i in range(len(query_tasks)):
        expired_in = (query_tasks[i].expired - datetime.now()).total_seconds()
        # check if the task will expired then logger the task title
        expired_soon = True if 0 < expired_in <= 900 else False
        if expired_soon:
            app.logger.info(f"{query_tasks[i].title} will expired in 15 minutes")
            
        # append the tasks from the query_task to the list to be return
        tasks.append({
            "title": query_tasks[i].title,
            "description": query_tasks[i].description,
            "expired": query_tasks[i].expired.strftime("%d/%m/%Y %H:%M"),
            "expired_in_15_mins": expired_soon
        })
    return jsonify({"result": tasks}), 200


# fetch all the tasks that haven't expired
@app.route("/tasks/all_non_expired", methods=['GET'])
def get_all_tasks_non_expired():
    tasks = []
    current_time = datetime.now()
    
    # query the tasks that the expired is more than current time
    # and order ascending by the column expired
    query_tasks = Tasks.query.filter(Tasks.expired > current_time).order_by(asc(Tasks.expired)).all()
    
    # if tasks not found return empty list
    if query_tasks == None:
        return jsonify({
            "result": tasks
        }), 200
    
    for i in range(len(query_tasks)):
        expired_in = (query_tasks[i].expired - current_time).total_seconds()
        # check if the task will expired then logger the task title
        expired_soon = True if 0 < expired_in <= 900 else False
        if expired_soon:
            app.logger.info(f"{query_tasks[i].title} will expired in 15 minutes")
            
        # append the tasks from the query_task to the list to be return
        tasks.append({
            "title": query_tasks[i].title,
            "description": query_tasks[i].description,
            "expired": query_tasks[i].expired.strftime("%d/%m/%Y %H:%M"),
            "expired_in_15_mins": expired_soon
        })
    return jsonify({"result": tasks}), 200
    
    
# fetch single data based on the task_id
@app.route("/task/<task_id>", methods=['GET'])
def get_task(task_id):
    # query the task with condition of the task_id
    task = Tasks.query.filter_by(task_id=task_id).first()
    current_time = datetime.now().replace(tzinfo=pytz.timezone('Asia/Hong_Kong'))
    if task == None:
        return jsonify({
            'result': f"task ID {task_id} not found"
        }), 404
    expired_in = (task.expired - datetime.now()).total_seconds()
    # check if the task will expired then logger the task title
    expired_soon = True if 0 < expired_in <= 900 else False
    if expired_soon:
        app.logger.info(f"{task.title} will expire in 15 minutes")
    return jsonify({
        'result': {
            "title": task.title,
            "description": task.description,
            "expired": task.expired.strftime("%d/%m/%Y %H:%M"),
            "expired_in_15_mins": expired_soon
        }
    }), 200


# create a task if task already expired refuse to enter db
@app.route("/create_task", methods=['POST'])
def create_task():
    # get the request in json format
    req = request.get_json()
    current_time = datetime.now(tz=tz)
    
    # return error if one of the fields are not fulfilled
    if 'task_id' not in req or 'title' not in req or 'description' not in req or 'expired' not in req:
        return jsonify({"result": "Please fill all the task_id, title, description, and expired"}), 400
    
    #convert expired date to datetime with hong kong timezone
    req['expired'] = datetime.strptime(
        req['expired'], '%d/%m/%Y %H:%M').replace(tzinfo=tz)
    
    # check if the task already exists in db
    found_task = Tasks.query.filter(or_(Tasks.task_id == req['task_id'],
        and_(Tasks.title == req['title'], Tasks.expired == req['expired']))).first()
    # check if task has already in db
    if found_task:
        return jsonify({
            "result": "You have put this task suggest to update instead of create new"
        }), 400
    # check if the request expired has already expired
    if req['expired'] < current_time:
        return jsonify({
            'result': f"sorry but your task has already expired"
        }), 400
        
    # insert data to db
    task = Tasks(req['task_id'], req['title'], req['description'], req['expired'])
    db.session.add(task)
    # commit the session after data is inserted to db
    db.session.commit()
    return jsonify({
        "result": f"task_id {req['task_id']} has been added"
    }), 201


# create bulk tasks
@app.route("/create_bulk_tasks", methods=['POST'])
def create_bulk_tasks():
    req = request.get_json()
    messages = []
    current_time = datetime.now(tz=tz)
    for i in range(len(req)):
        if 'task_id' not in req[i] or 'title' not in req[i] or 'description' not in req[i] or 'expired' not in req[i]:
            messages.append(
                f"Please fill all the title, description, and expired for request {i+1}")
        else:
            req[i]['expired'] = datetime.strptime(
                req[i]['expired'], '%d/%m/%Y %H:%M').replace(tzinfo=tz)
            found_task = Tasks.query.filter(or_(Tasks.task_id == req[i]['task_id'], 
                and_(Tasks.title == req[i]['title'], Tasks.expired == req[i]['expired']))).first()
            # check if task has already in the db
            if found_task:
                messages.append(f"task with task_id {req[i]['task_id']} has existed in the db")
            # check if the request expired has already expired
            if req[i]['expired'] < current_time:
                messages.append(f"task with task_id {req[i]['task_id']} has already expired")
                
            # insert data to db
            task = Tasks(req[i]['task_id'], req[i]['title'], req[i]['description'], req[i]['expired'])
            db.session.add(task)
            messages.append(f"task_id {req[i]['task_id']} has been added")
    # commit the sessions after all the db inserted
    db.session.commit()
    return jsonify({
        "result": messages
    }), 201


# update task by id
@app.route("/update_task/<task_id>", methods=['PUT'])
def update_task(task_id):
    req = request.get_json()
    task = Tasks.query.filter_by(task_id=task_id).first()
    if task == None:
        return jsonify({
            "result": f"TaskID {task_id} not found"
        }), 404
    if 'title' in req and req['title'] != '':
        task.title = req['title']
    if 'description' in req and req['description'] != '':
        task.description = req['description']
    if 'expired' in req and req['expired'] != '':
        if req['expired'] < datetime.now():
            return jsonify({
                "result": "Please update the expired to later than now"
            })
        task.expired = datetime.strptime(
                req['expired'], '%d/%m/%Y %H:%M').replace(tzinfo=pytz.timezone('Asia/Hong_Kong'))
    # commit the update session
    db.session.commit()
    return jsonify({
        "result": f"TaskID {task_id} has been updated"
    }), 200


# delete task by id
@app.route("/delete_task/<task_id>", methods=['DELETE'])
def remove_tasks_by_id(task_id):
    # remove task from the db
    task = Tasks.query.filter_by(task_id=task_id).delete()
    # if there is no task remove return 404
    if task == 0:
        return jsonify({
            'result': f"task ID {task_id} not found"
        }), 404
    # commit the delete session
    db.session.commit()
    return jsonify({
        'result': f'task ID {task_id} has been deleted'
    }), 200
        
if __name__ == "__main__":
    app.run()
