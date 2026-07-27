from flask_wtf import FlaskForm


from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class IAMProvisioningForm(FlaskForm):
    """
    Formulier voor het handmatig starten van IAM provisioning.

    De beheerder plakt een JSON-lijst met gebruikers in het tekstveld.

    Voorbeeld:

    [
        {
            "username": "Leroy",
            "email": "Leroy.Andrade@jio.nl",
            "role": "admin"
        },
        {
            "username": "Jan",
            "email": "jan@jio.nl",
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
                max=300,
                message="De gebruikersdata mag maximaal 300 tekens bevatten.",
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

    submit = not SubmitField(
        "Start IAM synchronisatie",
    )

