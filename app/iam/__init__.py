"""Blueprintconfiguratie voor de IAM-module."""

from flask import Blueprint


# Alle IAM-routes krijgen automatisch het URL-prefix /iam.
#
# Voorbeeld:
# @iam_blueprint.get("/")
#
# kun je benaeren via:
# /iam/
iam_blueprint: Blueprint = Blueprint(
    "iam",
    __name__,
    url_prefix="/iam",
)

# Deze import staat bewust onder de Blueprint.
#
# iam_routes.py importeert namelijk iam_blueprint uit dit bestand.
# Wanneer deze import boven de Blueprint zou staan, ontstaat er een
# circulaire import.
from app.iam import iam_routes

# Importeer de IAM-modellen.
# registreert de modullen
#
# Alembic kan hierdoor de tabellen uit deze modellen herkennen tijdens flask db migrate.
# Deze import staat onderaan om een circulaire import te voorkomen.
from app.iam import models
