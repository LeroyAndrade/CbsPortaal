"""Databasemodel voor IAM-provisioningevents."""

from datetime import datetime, timezone

from app.extensions import db


class IamProvisioningEvent(db.Model):
    """
    Bewaar een gebeurtenis uit het IAM-provisioningproces.

    Iedere synchronisatie kan één of meerdere provisioningevents
    opleveren, zoals het aanmaken, bijwerken of verwijderen van
    een gebruiker.
    """

    __tablename__ = "iam_provisioning_events"

    # Unieke primaire sleutel van het provisioningevent.
    id = db.Column(
        db.Integer,  primary_key=True,
    )

    # E-mailadres van de gebruiker waarop de actie is uitgevoerd.
    email = db.Column(
        db.String(255),  nullable=False,
    )

    # Uitgevoerde provisioningactie.
    #
    # Mogelijke waarden:
    # - created
    # - updated
    # - deleted
    # - failed
    action = db.Column(
        db.String(50),  nullable=False,
    )

    # Beschrijving van de uitgevoerde provisioningactie.
    message = db.Column(
        db.String(255),  nullable=False,
    )

    # Tijdstip waarop het provisioningevent is geregistreerd.
    created_at = db.Column(
        db.DateTime(timezone=True),  nullable=False,  default=lambda: datetime.now(timezone.utc),
    )

    def __init__(self, email: str, action: str, message: str) -> None:
        """Initialiseer een nieuw provisioningevent."""

        # Sla het e-mailadres van de gebruiker op.
        self.email = email

        # Sla de uitgevoerde provisioningactie op.
        self.action = action

        # Sla de beschrijving van de actie op.
        self.message = message