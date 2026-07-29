from flask_wtf import FlaskForm


from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

# from iam.models import IAMProvisioningEvent

class IAMProvisioningForm(FlaskForm):
    """
    Voorbeeld:

    [
        {
            "username": "Leroy.Andrade",
            "email": "Leroy.Andrade@jio.nl",
            "password": "SterkWachtwoord123!",
            "role": "admin"
        },
        {
            "username": "Pietje.Puk",
            "email": "Pietje.Puk@jio.nl",
            "password": "SterkWachtwoord1234!",
            "role": "user"
        }
    ]

    Het formulier controleert alleen of er invoer aanwezig is.

    Het controleren van geldige JSON en het verwerken van gebruikers
    gebeurt later in de IAM-service. Hierdoor blijft het formulier
    verantwoordelijk voor formulierinvoer en niet voor businesslogica.

    """

    source_data = TextAreaField(
        "Gebruikersdata in JSON-formaat",
        validators=[
            DataRequired(
                message="Voer gebruikersdata in.",
            ),
            Length(
                max=3000,
                message="De gebruikersdata mag maximaal 3000 tekens bevatten.",
            ),
        ],
        render_kw={
            "placeholder": (
                '[\n'
                '    {\n'
                '        "username": "Leroy",\n'
                '        "email": "Leroy.Andrade@jio.nl",\n'
                '        "role": "admin"\n'
                '    }\n'
                ']'
            ),
            "rows": 18,
            "spellcheck": "false",
        },
    )

    submit = SubmitField(
        "Start IAM synchronisatie",
    )


# los

"""
[
   {
            "username": "Leroy.Andrade",
            "email": "Leroy.Andrade@jio.nl",
            "password": "SterkWachtwoord123!",
            "role": "admin"
    }
]


"""
# if reboot
# iam_forms
# iam_routes
# iam_provisioning_service
# user.py