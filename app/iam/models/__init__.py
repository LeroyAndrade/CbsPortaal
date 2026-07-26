"""
Importeer alle IAM-modellen.

Door dit model hier te importeren weet SQLAlchemy dat dit model
bestaat zodra de IAM-module wordt geladen.

Alembic gebruikt deze metadata tijdens het maken van migraties.
"""

from app.iam.models.iam_provisioning_event import IamProvisioningEvent

