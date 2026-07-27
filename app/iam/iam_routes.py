"""HTTP-routes voor de IAM-module."""

from flask import abort, flash, render_template
from flask_login import current_user, login_required

from app.extensions.db import db
from app.iam import iam_blueprint
from app.iam.iam_forms import IAMProvisioningForm
from app.models.user import User


@iam_blueprint.route("/", methods=["GET", "POST"])
@login_required
def iam_index() -> str:
    """
    Toon de startpagina van de IAM-module.

    Alleen gebruikers met de rol admin mogen deze pagina openen.

    De route haalt voorlopig alleen de gebruikers op en toont
    het IAM-formulier. De provisioninglogica blijft in de service.
    """

    # Stop het verzoek direct wanneer de ingelogde gebruiker
    # geen beheerder is.
    #
    # Hierdoor wordt de IAM-pagina niet eerst opgebouwd voor
    # gebruikers die geen toegang hebben.
    if current_user.role != "admin":
        abort(
            403,
            description="Je hebt geen toegang tot de IAM-module.",
        )

    # Maak het formulier aan dat later de provisioninggegevens
    # naar de IAM-service doorstuurt.
    form = IAMProvisioningForm()

    # Haal alle gebruikers op via de SQLAlchemy-sessie.
    #
    # Deze vorm voorkomt de IDE-waarschuwing die soms verschijnt
    # bij het gebruik van User.query.
    users = db.session.execute(
        db.select(User)
    ).scalars().all()

    # Toon tijdelijk een melding zodat duidelijk is dat
    # de beheerder toegang heeft gekregen.
    flash(
        "Hallo admin.",
        "success",
    )

    return render_template(
        "iam/iam_index.html",
        users=users,
        form=form,
    )