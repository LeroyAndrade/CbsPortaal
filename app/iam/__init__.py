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
from app.iam import iam_routes  # noqa: E402, F401