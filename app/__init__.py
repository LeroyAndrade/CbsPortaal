from flask import Flask
from config import Config

from app.extensions import db, migrate, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Extensies init
    db.init_app(app)
    migrate.init_app(app, db)

    # Blueprint init
    from .routes import bp
    app.register_blueprint(bp)

    return app