from flask import (Blueprint,
                   render_template,
                   redirect,
                   request,
                   url_for)

from app.database import get_db

main = Blueprint("main", __name__)

@main.route("/")
def home():
    return render_template("index.html")

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