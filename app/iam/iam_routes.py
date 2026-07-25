"""HTTP-routes voor de IAM-module."""

from flask import render_template

from app.iam import iam_blueprint


@iam_blueprint.get("/")
def iam_index() -> str:
    """
    Toon de startpagina van de IAM-module.

    Deze route bevat nog geen database- of businesslogica.
    Dat voegen we in latere commits toe.
    """

    return render_template(
        "iam/iam_index.html",
    )