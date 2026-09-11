import os

from flask import Flask, render_template

from app import database


def create_app():
    app = Flask(__name__)
    
    app.config["SECRET_KEY"] = "dev-secret-key"

    app.config["DATABASE"] = os.path.join(
        app.instance_path,
        "devboard.sqlite"
    )

    os.makedirs(app.instance_path, exist_ok=True)

    database.init_app(app)

    from app.routes import main
    app.register_blueprint(main)
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404


    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("500.html"), 500

    return app