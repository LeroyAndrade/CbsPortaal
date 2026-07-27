import json
import logging
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from models import User


class IAMProvisioningService:
    """
    Verwerk gebruikersgegevens die via de IAM-module worden aangeleverd.

    De routes hoeven hierdoor geen database- of provisioninglogica
    te bevatten. De route ontvangt straks alleen het formulier en geeft
    de JSON-tekst door aan deze service.

    Ondersteunde acties:

    - upsert:
      Maak een gebruiker aan of werk een bestaande gebruiker bij.

    - activate:
      Activeer een bestaande gebruiker.

    - deactivate:
      Deactiveer een bestaande gebruiker.

    Wanneer geen action is opgegeven, gebruikt de service automatisch
    de actie upsert.
    """

    # Alleen deze velden mogen vanuit het IAM-verzoek rechtstreeks
    # op een gebruiker worden ingevuld.
    #
    # Hiermee voorkomen we dat een IAM-verzoek bijvoorbeeld het ID,
    # wachtwoord of andere interne databasevelden kan aanpassen.
    ALLOWED_USER_FIELDS: set[str] = {
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
    }

    # Alleen deze acties worden door de provisioningservice geaccepteerd.
    ALLOWED_ACTIONS: set[str] = {
        "upsert",
        "activate",
        "deactivate",
    }

    @staticmethod
    def provision(raw_json: str) -> dict[str, Any]:
        s
        """
        Verwerk alle gebruikers uit een JSON-verzoek.

        De volledige batch wordt als één database-transactie verwerkt.

        Wanneer bij één gebruiker een onverwachte databasefout ontstaat,
        wordt de volledige transactie teruggedraaid. Hierdoor wordt nooit
        slechts een gedeelte van een provisioningbatch opgeslagen.
        """

        # Zet de tekst uit het formulier eerst om naar Python-data.
        records = IAMProvisioningService._parse_json(raw_json)

        # Houd bij hoeveel acties binnen de batch zijn uitgevoerd.
        result: dict[str, Any] = {
            "created": 0,
            "updated": 0,
            "activated": 0,
            "deactivated": 0,
            "failed": 0,
            "messages": [],
        }

        try:
            for record in records:
                try:
                    action = IAMProvisioningService._get_action(record)
                    message = IAMProvisioningService._process_record(record, action)

                    # Verhoog de teller die hoort bij de uitgevoerde actie.
                    result[message["result"]] += 1
                    result["messages"].append(message["message"])

                except ValueError as error:
                    # Een validatiefout van één record hoeft de overige
                    # records uit dezelfde batch niet te blokkeren.
                    #
                    # De mislukte actie wordt wel als provisioningevent
                    # opgeslagen, zodat beheerders de fout later kunnen zien.
                    email = IAMProvisioningService._get_event_email(record)
                    error_message = str(error)

                    IAMProvisioningService._add_event(
                        email=email,
                        action="failed",
                        message=error_message,
                    )

                    result["failed"] += 1
                    result["messages"].append(error_message)

            # Sla alle gebruikerswijzigingen en provisioningevents
            # gezamenlijk op.
            db.session.commit()

            return result

        except SQLAlchemyError as error:
            # Draai alle nog niet opgeslagen wijzigingen terug wanneer
            # SQLAlchemy of de database een onverwachte fout geeft.
            db.session.rollback()

            logging.exception(
                "Databasefout tijdens IAM-provisioning."
            )

            raise RuntimeError(
                "De IAM-provisioning kon niet in de database worden opgeslagen."
            ) from error

    @staticmethod
    def _parse_json(raw_json: str) -> list[dict[str, Any]]:
        """
        Zet de ontvangen JSON-tekst om naar een lijst gebruikersrecords.

        Ondersteunde structuren:

        Eén gebruiker:
        {
            "email": "gebruiker@example.nl"
        }

        Een lijst gebruikers:
        [
            {
                "email": "gebruiker@example.nl"
            }
        ]

        Een object met een users-lijst:
        {
            "users": [
                {
                    "email": "gebruiker@example.nl"
                }
            ]
        }
        """

        if raw_json is None or raw_json.strip() == "":
            raise ValueError(
                "De provisioninggegevens mogen niet leeg zijn."
            )

        try:
            payload = json.loads(raw_json)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"De provisioninggegevens bevatten ongeldige JSON op regel {error.lineno}."
            ) from error

        # Een los gebruikersobject wordt intern omgezet naar een lijst
        # met één record.
        if isinstance(payload, dict) and "users" not in payload:
            records = [payload]

        # Een object met de sleutel users gebruikt de waarde van users.
        elif isinstance(payload, dict):
            records = payload.get("users")

        # Een JSON-lijst kan direct worden verwerkt.
        elif isinstance(payload, list):
            records = payload

        else:
            raise ValueError(
                "De JSON moet een gebruiker, een gebruikerslijst of een object met users bevatten."
            )

        if not isinstance(records, list):
            raise ValueError(
                "Het veld users moet een lijst zijn."
            )

        if len(records) == 0:
            raise ValueError(
                "De provisioninggegevens bevatten geen gebruikers."
            )

        for record in records:
            if not isinstance(record, dict):
                raise ValueError(
                    "Iedere gebruiker in de provisioninglijst moet een JSON-object zijn."
                )

        return records

    @staticmethod
    def _get_action(record: dict[str, Any]) -> str:
        """
        Lees en controleer de gevraagde provisioningactie.

        Wanneer action ontbreekt, wordt upsert gebruikt.
        """

        action = record.get("action", "upsert")

        if not isinstance(action, str):
            raise ValueError(
                "Het veld action moet tekst bevatten."
            )

        action = action.strip().lower()

        if action not in IAMProvisioningService.ALLOWED_ACTIONS:
            raise ValueError(
                f"Onbekende IAM-actie: {action}."
            )

        return action

    @staticmethod
    def _process_record(record: dict[str, Any], action: str) -> dict[str, str]:
        """
        Stuur één gebruikersrecord naar de juiste interne methode.
        """

        email = IAMProvisioningService._get_required_email(record)

        if action == "upsert":
            return IAMProvisioningService._upsert_user(
                email=email,
                record=record,
            )

        if action == "activate":
            return IAMProvisioningService._set_user_active(
                email=email,
                active=True,
            )

        return IAMProvisioningService._set_user_active(
            email=email,
            active=False,
        )

    @staticmethod
    def _upsert_user(email: str, record: dict[str, Any]) -> dict[str, str]:
        """
        Maak een gebruiker aan of werk een bestaande gebruiker bij.
        """

        user = User.query.filter_by(
            email=email,
        ).first()

        if user is None:
            user = User()

            # Vul eerst de door IAM toegestane gebruikersvelden in.
            IAMProvisioningService._apply_user_fields(
                user=user,
                record=record,
            )

            # Een nieuw account krijgt standaard de rol user wanneer
            # de IAM-data geen expliciete rol bevat.
            IAMProvisioningService._set_default_role(user)

            # Maak een niet te raden intern wachtwoord aan wanneer
            # het User-model een wachtwoordkolom heeft.
            #
            # Het wachtwoord wordt niet teruggegeven of gelogd.
            # De gebruiker kan daardoor niet met dit willekeurige
            # systeemwachtwoord inloggen.
            IAMProvisioningService._set_random_password(user)

            # Activeer een nieuw account standaard wanneer het model
            # een active- of is_active-kolom bevat.
            IAMProvisioningService._write_active_value(
                user=user,
                active=True,
            )

            db.session.add(user)

            message = f"Gebruiker {email} is aangemaakt."

            IAMProvisioningService._add_event(
                email=email,
                action="created",
                message=message,
            )

            return {
                "result": "created",
                "message": message,
            }

        # Werk alleen de toegestane velden bij.
        IAMProvisioningService._apply_user_fields(
            user=user,
            record=record,
        )

        message = f"Gebruiker {email} is bijgewerkt."

        IAMProvisioningService._add_event(
            email=email,
            action="updated",
            message=message,
        )

        return {
            "result": "updated",
            "message": message,
        }

    @staticmethod
    def _set_user_active(email: str, active: bool) -> dict[str, str]:
        """
        Activeer of deactiveer een bestaande gebruiker.
        """

        user = User.query.filter_by(
            email=email,
        ).first()

        if user is None:
            raise ValueError(
                f"Gebruiker {email} bestaat niet en kan daarom niet worden gewijzigd."
            )

        # Schrijf de status alleen naar een echte databasekolom.
        #
        # Een eigenschap van bijvoorbeeld Flask-Login mag hier niet
        # per ongeluk worden overschreven.
        status_updated = IAMProvisioningService._write_active_value(
            user=user,
            active=active,
        )

        if status_updated is False:
            raise ValueError(
                "Het User-model heeft geen active- of is_active-kolom."
            )

        if active is True:
            result = "activated"
            action = "activated"
            message = f"Gebruiker {email} is geactiveerd."

        else:
            result = "deactivated"
            action = "deactivated"
            message = f"Gebruiker {email} is gedeactiveerd."

        IAMProvisioningService._add_event(
            email=email,
            action=action,
            message=message,
        )

        return {
            "result": result,
            "message": message,
        }

    @staticmethod
    def _apply_user_fields(user: User, record: dict[str, Any]) -> None:
        """
        Kopieer alleen toegestane én bestaande databasevelden.

        De controle via User.__table__.columns voorkomt dat eigenschappen
        of methodes buiten het SQLAlchemy-model worden overschreven.
        """

        user_columns = set(User.__table__.columns.keys())

        for field_name in IAMProvisioningService.ALLOWED_USER_FIELDS:
            if field_name not in user_columns:
                continue

            if field_name not in record:
                continue

            value = record.get(field_name)

            # Het e-mailadres wordt altijd genormaliseerd naar kleine letters.
            if field_name == "email" and isinstance(value, str):
                value = value.strip().lower()

            # Tekstwaarden worden aan de randen opgeschoond.
            elif isinstance(value, str):
                value = value.strip()

            setattr(
                user,
                field_name,
                value,
            )

        # Wanneer het model een username vereist en IAM geen username
        # meestuurt, gebruiken we het gedeelte voor het @-teken.
        if "username" in user_columns:
            username = getattr(user, "username", None)

            if username is None or str(username).strip() == "":
                email = str(record.get("email", "")).strip().lower()

                setattr(
                    user,
                    "username",
                    email.split("@", 1)[0],
                )

    @staticmethod
    def _set_default_role(user: User) -> None:
        """
        Geef nieuwe gebruikers standaard de rol user.
        """

        user_columns = set(User.__table__.columns.keys())

        if "role" not in user_columns:
            return

        role = getattr(user, "role", None)

        if role is None or str(role).strip() == "":
            setattr(
                user,
                "role",
                "user",
            )

    @staticmethod
    def _set_random_password(user: User) -> None:
        """
        Stel voor een nieuw account een willekeurig intern wachtwoord in.

        De service ondersteunt zowel een set_password-methode als veel
        gebruikte kolomnamen voor een wachtwoordhash.
        """

        random_password = secrets.token_urlsafe(32)

        # Gebruik de bestaande methode van het User-model wanneer die bestaat.
        if callable(getattr(user, "set_password", None)):
            user.set_password(random_password)
            return

        user_columns = set(User.__table__.columns.keys())
        password_hash = generate_password_hash(random_password)

        if "password_hash" in user_columns:
            setattr(
                user,
                "password_hash",
                password_hash,
            )

        elif "password" in user_columns:
            setattr(
                user,
                "password",
                password_hash,
            )

    @staticmethod
    def _write_active_value(user: User, active: bool) -> bool:
        """
        Schrijf de accountstatus naar een ondersteunde databasekolom.

        Geeft True terug wanneer een statuskolom is gevonden.
        Geeft False terug wanneer het model geen statuskolom heeft.
        """

        user_columns = set(User.__table__.columns.keys())

        if "is_active" in user_columns:
            setattr(
                user,
                "is_active",
                active,
            )

            return True

        if "active" in user_columns:
            setattr(
                user,
                "active",
                active,
            )

            return True

        return False

    @staticmethod
    def _get_required_email(record: dict[str, Any]) -> str:
        """
        Lees en controleer het verplichte e-mailadres.
        """

        email = record.get("email")

        if not isinstance(email, str):
            raise ValueError(
                "Iedere IAM-gebruiker moet een e-mailadres bevatten."
            )

        email = email.strip().lower()

        # Dit is bewust een eenvoudige controle.
        #
        # De service controleert hier alleen of de minimale vorm aanwezig is.
        # Uitgebreide e-mailvalidatie hoort bij het formulier of de bron
        # die de provisioninggegevens aanlevert.
        if email == "" or "@" not in email:
            raise ValueError(
                f"Ongeldig e-mailadres: {email or 'leeg'}."
            )

        return email

    @staticmethod
    def _get_event_email(record: dict[str, Any]) -> str:
        """
        Bepaal welk e-mailadres bij een mislukt event wordt opgeslagen.

        Het databaseveld email is verplicht. Wanneer geen geldig adres
        beschikbaar is, gebruiken we daarom een herkenbare systeemwaarde.
        """

        email = record.get("email")

        if isinstance(email, str) and email.strip() != "":
            return email.strip().lower()

        return "onbekend@iam.local"

    @staticmethod
    def _add_event(email: str, action: str, message: str) -> None:
        """
        Voeg een provisioningevent toe aan de huidige transactie.

        Deze methode commit niet zelfstandig. Daardoor worden de
        gebruikerswijziging en het bijbehorende audit-event altijd
        gezamenlijk opgeslagen of gezamenlijk teruggedraaid.
        """

        event = IAMProvisioningEvent(
            email=email,
            action=action,
            message=message,
        )

        db.session.add(event)