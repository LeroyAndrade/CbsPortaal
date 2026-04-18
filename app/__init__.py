from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# db vanuit 1 centrale plek
# from app.extensions import db, migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Routes importeren
    from app.routes import main
    app.register_blueprint(main)

    return app



