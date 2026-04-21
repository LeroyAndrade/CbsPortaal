from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# voor Login
from flask_login import LoginManager

# db en migratie
db = SQLAlchemy()
migrate = Migrate()

# Voor login
login_manager = LoginManager()
login_manager.login_view = "main.login"