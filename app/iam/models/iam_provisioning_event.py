"""Databasemodel voor IAM-provisioningevents."""
# Importeer datetime en UTC om het tijdstip van een IAM-actie
# correct en met tijdzone op te slaan.
from datetime import datetime, UTC

# Importeer de bestaande SQLAlchemy database-extensie.
from app.extensions.db import db


class IAMProvisioningEvent(db.Model):
    """
    Sla een uitgevoerde IAM provisioningactie op.

    Dit model houdt bij wat het IAM-proces heeft uitgevoerd.

    Voorbeelden:
    - Een gebruiker is aangemaakt.
    - Een gebruiker is bijgewerkt.
    - Een gebruiker is gedeactiveerd.
    - Een gebruiker is opnieuw geactiveerd.
    - Een provisioningactie is mislukt.
    """

    # Geef de database tabel een vaste en duidelijke naam.
    __tablename__ = "iam_provisioning_events"

    # Uniek nummer van het provisioningevent.
    #
    # primary_key=True betekent dat iedere database regel
    # een uniek ID krijgt.
    id = db.Column(
        db.Integer,  primary_key=True,
    )

    # E-mailadres van de gebruiker waarop de IAM-actie
    # betrekking heeft.
    #
    # nullable=False betekent dat dit veld verplicht is.
    email = db.Column(
        db.String(255),  nullable=False,
    )

    # Naam van de uitgevoerde IAM-actie.
    #
    # Voorbeelden:
    # - created
    # - updated
    # - activated
    # - deactivated
    # - failed
    action = db.Column(
        db.String(50),  nullable=False,
    )

    # Leesbare beschrijving van de uitgevoerde actie.
    #
    # Hierdoor kan een beheerder later begrijpen
    # wat het IAM-proces precies heeft gedaan.
    message = db.Column(
        db.String(255),  nullable=False,
    )

    # Datum en tijd waarop het provisioningevent
    # in de database is opgeslagen.
    #
    # timezone=True zorgt ervoor dat SQLAlchemy rekening
    # houdt met tijdzones.
    #
    # datetime.now(UTC) slaat het tijdstip in UTC op.
    created_at = db.Column(
        db.DateTime(timezone=True),  nullable=False,  default=lambda: datetime.now(UTC),
    )

    def __init__(self, email: str, action: str, message: str) -> None:
        """
        Maak een nieuw IAM provisioningevent aan.

        email:
        Het e-mailadres van de gebruiker.

        action:
        De naam van de uitgevoerde IAM-actie.

        message:
        Een leesbare beschrijving van de actie.
        """

        self.email = email
        self.action = action
        self.message = message