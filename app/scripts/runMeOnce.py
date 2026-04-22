# flask create-admin

import secrets
import string
from app import create_app
from app.models import User
from app.extensions import db

app = create_app()

with app.app_context():
    if User.query.filter_by(username='admin').first():
        print("User 'admin' bestaat al. Geen nieuwe user aangemaakt.")
    else:
        # random wachtwoord met 12 tekens
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for i in range(15))

        # User aanmaken
        admin = User(
            username="admin",
            email="admin@cbs.nl",
            password=password
        )

        db.session.add(admin)
        # Commit
        db.session.commit()

        print(
            f"Showing admin password one-time-only: {password} \nPlease make a note and store somewhere safe..."
        )