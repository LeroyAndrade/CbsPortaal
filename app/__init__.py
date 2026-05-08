from flask import Flask
from config import Config
from zoneinfo import ZoneInfo

from app.extensions import db, migrate, login_manager

# Krijg echte tijd van de user voor in de logging (seizoen ongebonden)
def local_time(dt):
    if dt is None:
        return ""

    return dt.astimezone(
        ZoneInfo("Europe/Amsterdam")
    ).strftime("%d-%m-%Y %H:%M")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes import bp
    app.jinja_env.filters["local_time"] = local_time
    app.register_blueprint(bp)



    return app



