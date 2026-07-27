# python -m app.scripts.runMeOnce
"""Maak éénmalig de eerste administrator aan."""

from getpass import getpass

from app import create_app
from app.extensions.db import db
from app.models.user import User


def create_admin() -> None:
    """Maak de eerste administrator aan."""

    app = create_app()

    with app.app_context():

        print("=== Dit script is bedoeld om slechts één keer uit te voeren. ===")

        if User.query.count() > 0:
            print("Er bestaat al een gebruiker. Dit script kan maar één keer worden uitgevoerd.")
            return

        username: str = input("Gebruikersnaam: ").strip()
        email: str = input("E-mailadres: ").strip().lower()

        # Vraag het wachtwoord op totdat het geldig is.
        while True:
            password: str = getpass("Wachtwoord: ")
            password_confirm: str = getpass("Herhaal wachtwoord: ")

            if password != password_confirm:
                print("❌ De wachtwoorden komen niet overeen. Probeer opnieuw.\n")
                continue

            if len(password) < 5:
                print("❌ Het wachtwoord moet minimaal 12 tekens bevatten.\n")
                continue

            break

        # Maak de administrator aan.
        admin: User = User(
            username=username,
            email=email,
            password=password,
            role="admin",
        )

        db.session.add(admin)
        db.session.commit()

        db.session.refresh(admin)

        print()
        print(f"Administrator '{admin.username}' is succesvol aangemaakt.")
        print(f"Rol: {admin.role}")


if __name__ == "__main__":
    create_admin()