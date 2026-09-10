from flask import (Blueprint,
                   abort,
                   render_template,
                   redirect,
                   request,
                   url_for,
                   flash)

from app.database import get_db

ALLOWED_PRIORITIES = {"low", "medium", "high"}
ALLOWED_PROJECT_STATUSES = {"active", "paused", "completed"}

main = Blueprint("main", __name__)

@main.route("/")
def home():
    db = get_db()

    total_tasks = db.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    pending_tasks = db.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE status = 'pending'
        """
    ).fetchone()[0]

    completed_tasks = db.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE status = 'completed'
        """
    ).fetchone()[0]

    total_projects = db.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    active_projects = db.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE status = 'active'
        """
    ).fetchone()[0]

    completed_projects = db.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE status = 'completed'
        """
    ).fetchone()[0]

    paused_projects = db.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE status = 'paused'
        """
    ).fetchone()[0]
    
    total_learning = db.execute(
        "SELECT COUNT(*) FROM learning_entries"
    ).fetchone()[0]

    in_progress_learning = db.execute(
        """
        SELECT COUNT(*)
        FROM learning_entries
        WHERE status = 'in_progress'
        """
    ).fetchone()[0]

    completed_learning = db.execute(
        """
        SELECT COUNT(*)
        FROM learning_entries
        WHERE status = 'completed'
        """
    ).fetchone()[0]

    average_progress = db.execute(
        """
        SELECT COALESCE(AVG(progress), 0)
        FROM learning_entries
        """
    ).fetchone()[0]

    return render_template(
        "index.html",
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        paused_projects=paused_projects,
        total_learning=total_learning,
        in_progress_learning=in_progress_learning,
        completed_learning=completed_learning,
        average_progress=round(average_progress),
    )

@main.route("/tasks")
def tasks():
    db = get_db()
    tasks = db.execute(
    """
    SELECT
        tasks.*,
        projects.name AS project_name

    FROM tasks

    LEFT JOIN projects
        ON tasks.project_id = projects.id

    ORDER BY tasks.created_at DESC
    """
    ).fetchall()
    return render_template("tasks.html", tasks=tasks)

def project_exists(project_id):
    if project_id is None:
        return True

    project = get_db().execute(
        "SELECT id FROM projects WHERE id = ?",
        (project_id,),
    ).fetchone()

    return project is not None

@main.route("/tasks/new", methods=("GET", "POST"))
def create_task():
    db = get_db()

    projects = db.execute(
        """
        SELECT id, name
        FROM projects
        WHERE status = 'active'
        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        priority = request.form["priority"]
        project_id = request.form.get("project_id")

        if not title:
            flash("Task title is required.", "error")

        elif priority not in ALLOWED_PRIORITIES:
            flash("Invalid task priority.", "error")

        else:
            if not project_id:
                project_id = None

            if not project_exists(project_id):
                flash("Selected project does not exist.", "error")
            else:
                db.execute(
                    """
                    INSERT INTO tasks (
                        title,
                        description,
                        priority,
                        project_id
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        title,
                        description,
                        priority,
                        project_id,
                    ),
                )

                db.commit()

                flash("Task created successfully.", "success")

                return redirect(url_for("main.tasks"))

    return render_template(
        "create_task.html",
        projects=projects,
    )


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

    db = get_db()

    projects = db.execute(
        """
        SELECT id, name
        FROM projects
        WHERE status = 'active'
        ORDER BY name
        """
    ).fetchall()

    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        priority = request.form["priority"]

        project_id = request.form.get("project_id")

        if not project_id:
            project_id = None

        if not title:
            flash("Task title is required.", "error")
        elif priority not in ALLOWED_PRIORITIES:
            flash("Invalid task priority.", "error")
        elif not project_exists(project_id):
            flash("Selected project does not exist.", "error")
        else:
            db.execute(
                """
                UPDATE tasks
                SET
                    title = ?,
                    description = ?,
                    priority = ?,
                    project_id = ?
                WHERE id = ?
                """,
                (
                    title,
                    description,
                    priority,
                    project_id,
                    task_id,
                ),
            )

            db.commit()
            flash("Task updated successfully.", "success")
            return redirect(url_for("main.tasks"))

    return render_template(
        "edit_task.html",
        task=task,
        projects=projects,
    )
    
    
@main.route('/tasks/<int:task_id>/complete', methods=('POST',))
def complete_task(task_id):
    get_task(task_id)
    
    db = get_db()
    
    db.execute(
        '''
        UPDATE tasks
        SET status = 'completed'
        WHERE id = ?
        ''',
        (task_id,),
    )
    flash("Task marked as completed.", "success")
    db.commit()
    
    return redirect(url_for('main.tasks'))


@main.route('/tasks/<int:task_id>/delete', methods=('POST',))
def delete_task(task_id):
    db = get_db()
    
    db.execute(
        '''
        Delete from tasks 
        Where id = ?
        ''',
        (task_id,),
    )
    
    db.commit()
    flash("Task deleted successfully.", "error")
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
        
        if not name:
            flash("Project name is required.", "error")
        else:
            db = get_db()
            
            db.execute(
                '''
                    INSERT INTO projects (name, description)
                    VALUES (?, ?)
                ''',
                (name, description),
            )
            
            db.commit()
            flash("Project created successfully.", "success")
            return redirect(url_for("main.projects"))
    
    return render_template("create_project.html")


def get_project(project_id):
    db = get_db()
    
    project = db.execute(
        '''
        SELECT * 
        FROM projects
        WHERE id = ?
        ''',
        (project_id,),
    ).fetchone()
    
    if project is None:
        abort(404)
        
    return project

@main.route('/projects/<int:project_id>/edit', methods=("GET", "POST"))
def edit_project(project_id):
    project = get_project(project_id)
    
    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form["description"].strip()
        status = request.form["status"]
        
        if not name:
            flash("Project name is required.", "error")
        elif status not in ALLOWED_PROJECT_STATUSES:
            flash("Invalid project status.", "error")
        else:
            db = get_db()
            
            db.execute(
                '''
                    UPDATE projects
                    SET name = ?, description = ?, status = ?
                    WHERE id = ?
                ''',
                (name, description, status, project_id)
            )
            
            db.commit()
            flash("Project updated successfully.", "success")
            return redirect(url_for('main.projects'))
    
    return render_template(
        'edit_project.html',
        project=project,
    )
    

@main.route("/projects/<int:project_id>/delete", methods=("POST",))
def delete_project(project_id):
    get_project(project_id)

    db = get_db()

    db.execute(
        "DELETE FROM projects WHERE id = ?",
        (project_id,),
    )

    db.commit()
    flash("Project deleted successfully.", "error")
    
    return redirect(url_for("main.projects"))

@main.route('/learning')
def learning():
    db = get_db()
    
    entries = db.execute(
        '''
        SELECT * 
        FROM learning_entries
        ORDER BY created_at DESC
        '''
    ).fetchall()
    
    return render_template(
        'learning.html',
        entries=entries
    )
    
@main.route("/learning/new", methods=("GET", "POST"))
def create_learning_entry():
    if request.method == "POST":
        topic = request.form["topic"].strip()
        category = request.form["category"].strip()
        notes = request.form["notes"].strip()

        try:
            progress = int(request.form["progress"])
        except ValueError:
            progress = -1

        status = request.form["status"]

        if not topic:
            flash("Learning topic is required.", "error")

        elif progress < 0 or progress > 100:
            flash("Progress must be between 0 and 100.", "error")

        elif status not in {
            "not_started",
            "in_progress",
            "completed",
        }:
            flash("Invalid learning status.", "error")
        
        elif status == "completed" and progress != 100:
            flash("Completed entries must have 100% progress.", "error")
        elif status == "not_started" and progress != 0:
            flash("Not started entries must have 0% progress.", "error")

        else:
            db = get_db()

            db.execute(
                """
                INSERT INTO learning_entries (
                    topic,
                    category,
                    progress,
                    status,
                    notes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    topic,
                    category,
                    progress,
                    status,
                    notes,
                ),
            )

            db.commit()

            flash(
                "Learning entry created successfully.",
                "success",
            )

            return redirect(url_for("main.learning"))

    return render_template("create_learning_entry.html")

def get_learning_entry(entry_id):
    entry = get_db().execute(
        "SELECT * FROM learning_entries WHERE id = ?",
        (entry_id,),
    ).fetchone()

    if entry is None:
        abort(404)

    return entry

@main.route("/learning/<int:entry_id>/edit", methods=("GET", "POST"))
def edit_learning_entry(entry_id):
    entry = get_learning_entry(entry_id)

    if request.method == "POST":
        topic = request.form["topic"].strip()
        category = request.form["category"].strip()
        notes = request.form["notes"].strip()

        try:
            progress = int(request.form["progress"])
        except ValueError:
            progress = -1

        status = request.form["status"]

        if not topic:
            flash("Learning topic is required.", "error")

        elif progress < 0 or progress > 100:
            flash("Progress must be between 0 and 100.", "error")

        elif status not in {
            "not_started",
            "in_progress",
            "completed",
        }:
            flash("Invalid learning status.", "error")

        elif status == "completed" and progress != 100:
            flash("Completed entries must have 100% progress.", "error")

        elif status == "not_started" and progress != 0:
            flash("Not started entries must have 0% progress.", "error")

        else:
            db = get_db()

            db.execute(
                """
                UPDATE learning_entries
                SET topic = ?,
                    category = ?,
                    progress = ?,
                    status = ?,
                    notes = ?
                WHERE id = ?
                """,
                (
                    topic,
                    category,
                    progress,
                    status,
                    notes,
                    entry_id,
                ),
            )

            db.commit()

            flash("Learning entry updated successfully.", "success")

            return redirect(url_for("main.learning"))

    return render_template(
        "edit_learning_entry.html",
        entry=entry,
    )
    
@main.route("/learning/<int:entry_id>/delete", methods=("POST",))
def delete_learning_entry(entry_id):
    get_learning_entry(entry_id)

    db = get_db()

    db.execute(
        "DELETE FROM learning_entries WHERE id = ?",
        (entry_id,),
    )

    db.commit()

    flash("Learning entry deleted successfully.", "success")

    return redirect(url_for("main.learning"))