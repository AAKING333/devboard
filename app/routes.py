from flask import (Blueprint,
                   abort,
                   render_template,
                   redirect,
                   request,
                   url_for)

from app.database import get_db

main = Blueprint("main", __name__)

@main.route("/")
def home():
    db = get_db()
    
    total_tasks = db.execute(
        '''
        Select COUNT(*)
        From tasks
        '''
    ).fetchone()[0]
    
    pending_tasks = db.execute(
        '''
        Select COUNT(*)
        From tasks
        Where status == 'pending'
        '''
    ).fetchone()[0]
    
    completed_tasks = db.execute(
            '''
            Select COUNT(*)
            From tasks
            Where status == 'completed'
            '''
        ).fetchone()[0]
    
    return render_template(
        "index.html",
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
        )

@main.route("/tasks")
def tasks():
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    return render_template("tasks.html", tasks=tasks)

@main.route("/tasks/new", methods=("GET", "POST"))
def create_task():
    if request.method == "POST":
        
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        priority = request.form['priority']
        
        if title:
            db = get_db()
            
            db.execute(
                '''
                INSERT INTO tasks (title, description, priority)
                VALUES (?, ?, ?)
                ''',
                
                (title, description, priority)
            )
            
            db.commit()
            
            return redirect(url_for('main.tasks'))
        
    return render_template('create_task.html')


def get_task(task_id):
    db = get_db()
    task = db.execute(
        "Select * from tasks Where id = ?",
        (task_id,),
    ).fetchone()
    
    if task is None:
        abort(404)
        
    return task


@main.route("/tasks/<int:task_id>/edit", methods=("GET", "POST"))
def edit_task(task_id):
    task = get_task(task_id)

    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        priority = request.form["priority"]

        if title:
            db = get_db()

            db.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?
                WHERE id = ?
                """,
                (title, description, priority, task_id),
            )

            db.commit()

            return redirect(url_for("main.tasks"))

    return render_template(
        "edit_task.html",
        task=task,
    )
    
    
@main.route('/tasks/<int:task_id>/complete', methods=('POST',))
def complete_task(task_id):
    get_task(task_id)
    
    db = get_db()
    
    db.execute(
        '''
        UPDATE tasks
        SET status == 'completed'
        WHERE id == ?
        ''',
        (task_id,),
    )
    
    db.commit()
    
    return redirect(url_for('main.tasks'))


@main.route('/tasks/<int:task_id>/delete', methods=('POST',))
def delete_task(task_id):
    db = get_db()
    
    db.execute(
        '''
        Delete from tasks 
        Where id == ?
        ''',
        (task_id,),
    )
    
    db.commit()
    
    return redirect(url_for('main.tasks'))


@main.route('/projects')
def projects():
    db = get_db()
    
    projects = db.execute('''
                            SELECT * 
                            FROM projects
                            ORDER BY created_at DESC
                          ''').fetchall()
    
    return render_template(
        "projects.html",
        projects=projects,
    )
    
@main.route('/projects/new', methods=('GET', 'POST'))
def create_project():
    if request.method == 'POST':
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        
        if name:
            db = get_db()
            
            db.execute(
                '''
                    InSERT INTO projects (name, description)
                    VALUES (?, ?)
                ''',
                (name, description),
            )
            
            db.commit()
            
            return redirect(url_for("main.projects"))
    
    return render_template("create_project.html")