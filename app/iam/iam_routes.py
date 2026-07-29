"""HTTP-routes voor de IAM-module."""

from flask import abort, flash, redirect, render_template, url_for, Response
from flask_login import current_user, login_required

from app.iam.services.iam_provisioning_service import (
    IAMProvisioningError,
    IAMProvisioningService,
)
from app.extensions.db import db
from app.iam import iam_blueprint
from app.iam.iam_forms import IAMProvisioningForm
from app.models.user import User
# Logging
from app.services.services import UserLog


@iam_blueprint.route("/", methods=["GET", "POST"])
@login_required
def iam_index() -> Response | str:
    UserLog.log_action(current_user, "IAM pagina bezocht")
    """
    Toon de startpagina van de IAM-module.

    Alleen gebruikers met de rol admin mogen deze pagina openen.

    De route behandelt uitsluitend HTTP-gerelateerde taken.
    Alle businesslogica blijft in IAMProvisioningService.
    """

    # Stop het verzoek direct wanneer de ingelogde gebruiker
    # geen beheerder is.
    if current_user.role != "admin":
        abort(
            403,
            description="U heeft onvoldoende rechten, neem contact op met de beheerder."
        )

    # Maak het provisioningformulier aan.
    form = IAMProvisioningForm()

    #
    # Verwerk een provisioningverzoek.
    #
    # De route valideert alleen het formulier.
    # De service verwerkt vervolgens alle businesslogica.
    #
    if form.validate_on_submit():

        try:
            result = IAMProvisioningService.provision(
                form.source_data.data,
            )

            flash(
                (
                    f"Provisioning voltooid. "
                    f"Aangemaakt: {result['created']}, "
                    f"Bijgewerkt: {result['updated']}."
                ),
                "success",
            )

            #
            # Gebruik het Post/Redirect/Get-patroon.
            #
            # Hierdoor wordt het formulier niet opnieuw
            # verzonden wanneer de gebruiker de pagina
            # ververst.
            #
            return redirect(
                url_for("iam.iam_index")
            )

        except IAMProvisioningError as error:

            flash(
                str(error),
                "danger",
            )

    # Haal de actuele gebruikers uit de database op.
    users = db.session.execute(
        db.select(User)
    ).scalars().all()

    return render_template(
        "iam/iam_index.html",
        current=current_user,
        current_user=current_user.username,
        users=users,
        form=form,
    )