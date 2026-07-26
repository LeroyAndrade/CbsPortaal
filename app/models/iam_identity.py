"""Databasemodel voor een IAM-identiteit."""

from datetime import datetime

from app.extensions.db import db


class IamIdentity(db.Model):
    """Een medewerker binnen het IAM-systeem."""

    __tablename__ = "iam_identity"

    id = db.Column(db.Integer, primary_key=True)

    department = db.Column(
        db.String(100),
        nullable=False,
    )

    first_name = db.Column(
        db.String(100),
        nullable=False,
    )

    last_name = db.Column(
        db.String(100),
        nullable=False,
    )

    username = db.Column(
        db.String(200),
        nullable=False,
        unique=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    roles = db.relationship(
        "IamIdentityRole",
        back_populates="identity",
        cascade="all, delete-orphan",
    )

    @property
    def full_name(self) -> str:
        """Geef de volledige naam terug."""

        return f"{self.first_name} {self.last_name}"