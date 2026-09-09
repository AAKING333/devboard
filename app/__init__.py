import os

from flask import Flask

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

    return app