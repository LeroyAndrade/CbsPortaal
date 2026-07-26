"""HTTP-routes voor de IAM-module."""

from flask import abort, render_template
from flask_login import current_user, login_required
from sqlalchemy.testing.suite.test_reflection import users

from app.iam import iam_blueprint


@iam_blueprint.get("/iam")
@login_required
def iam_index() -> str:
    """
    Toon de startpagina van de IAM-module.

    Deze route bevat nog geen database- of businesslogica.
    Dat voegen we in latere commits toe.
    """
    if current_user.role != "admin":
        abort(403)
        flask.abort("SIlence is golden")

    return render_template(
        "iam/iam_index.html",
        users=users)
