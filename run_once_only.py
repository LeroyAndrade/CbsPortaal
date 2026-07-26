
# python -m app.scripts.runMeOnce
"""Maak éénmalig de eerste administrator aan."""

from getpass import getpass

from app import create_app
from app.extensions.db import db
from app.models.user import User


def create_admin() -> None:
    """Maak eerste administrator aan."""

    app = create_app()

    with app.app_context():

        print("=== Dit script is bedoeld om slechts één keer uit te voeren. ===")

        if User.query.count() > 0:
            print("Er bestaat al een gebruiker. Dit script kan maar één keer worden uitgevoerd.")
            return

        username: str = input("Gebruikersnaam: ").strip()
        email: str = input("E-mailadres: ").strip().lower()
        password: str = getpass("Wachtwoord: ")

        # Maak de administrator aan.
        admin: User = User(
            username=username,
            email=email,
            password=password,
            role="admin",
        )

        db.session.add(admin)
        db.session.commit()

        print()
        print(f"Administrator '{username}' is succesvol aangemaakt.")


if __name__ == "__main__":
    create_admin()