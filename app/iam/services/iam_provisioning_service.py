"""Businesslogica voor het provisionen van gebruikers."""

import json
from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions.db import db
from app.models.user import User

class IAMProvisioningError(Exception):
    """
    Fout die tijdens IAM-provisioning kan ontstaan.

    De route kan deze fout later afvangen en als een duidelijke
    melding aan de beheerder tonen.
    """


class IAMProvisioningService:
    """
    Maak gebruikers aan of werk bestaande gebruikers bij.

    Deze service bevat uitsluitend businesslogica.

    Zaken zoals formulieren, redirects en flashmeldingen horen
    niet in deze service. Die blijven in de Flask-route.
    """

    REQUIRED_FIELDS = {
        "username",
        "email",
        "role",
    }

    @classmethod
    def provision(cls, source_data: str) -> dict[str, int]:
        """
        Verwerk JSON met één gebruiker of meerdere gebruikers.

        Voorbeeld van één gebruiker:

        {
            "username": "testuser",
            "email": "testuser@example.nl",
            "password": "SterkWachtwoord123!",
            "role": "user"
        }

        Een lijst met meerdere gebruikers wordt ook ondersteund.
        """

#000  JSON verwerken
        users_data = cls._parse_source_data(source_data)


# 010 Teller voor rapportage
        created_count = 0
        updated_count = 0

        try:
            for position, raw_user_data in enumerate(
                users_data,
                start=1,
            ):

# 020 Valideer gebruiker
                user_data = cls._validate_user_data(
                    user_data=raw_user_data,
                    position=position,
                )

#003 Bestaande gebruiker zoeken
                existing_user = cls._find_user_by_email(
                    email=user_data["email"],
                )


#004 Nieuwe gebruiker of bestaande gebruiker bijwerken
                if existing_user is None:
                    cls._create_user(
                        user_data=user_data,
                        position=position,
                    )

                    created_count += 1

                else:
                    cls._update_user(
                        user=existing_user,
                        user_data=user_data,
                        position=position,
                    )

                    updated_count += 1

            # Flush voert de SQL-statements uit zonder de transactie
            # al definitief op te slaan.
            #
            # Daardoor worden databasefouten nog binnen deze
            # try/except gevonden.
            db.session.flush()

            # De volledige invoer wordt als één transactie opgeslagen.
            #
            # Als één gebruiker mislukt, wordt niets opgeslagen.

#005
            db.session.commit()

        except IAMProvisioningError:
            db.session.rollback()
            raise

        except IntegrityError as error:
            db.session.rollback()

            raise IAMProvisioningError(
                "Een gebruikersnaam of e-mailadres is al in gebruik."
            ) from error

        except SQLAlchemyError as error:
            db.session.rollback()

            raise IAMProvisioningError(
                "De gebruikers konden niet in de database "
                "worden opgeslagen."
            ) from error

        return {
            "created": created_count,
            "updated": updated_count,
            "total": len(users_data),
        }


#011
    @staticmethod
    def _parse_source_data(
        source_data: str,
    ) -> list[dict[str, Any]]:
        """
        Zet JSON-tekst om naar een lijst met gebruikers.

        Eén los JSON-object wordt intern omgezet naar een lijst
        met één gebruiker.
        """

        try:
            parsed_data = json.loads(source_data)

        except json.JSONDecodeError as error:
            raise IAMProvisioningError(
                f"Ongeldige JSON op regel {error.lineno}, "
                f"kolom {error.colno}: {error.msg}."
            ) from error

        if isinstance(parsed_data, dict):
            parsed_data = [parsed_data]

        if not isinstance(parsed_data, list):
            raise IAMProvisioningError(
                "De JSON moet één gebruiker of een lijst "
                "met gebruikers bevatten."
            )

        if not parsed_data:
            raise IAMProvisioningError(
                "De JSON bevat geen gebruikers."
            )

        return parsed_data

    @classmethod
    def _validate_user_data(
        cls,
        user_data: Any,
        position: int,
    ) -> dict[str, str | None]:
        """
        Controleer en normaliseer één gebruikersrecord.
        """

        if not isinstance(user_data, dict):
            raise IAMProvisioningError(
                f"Gebruiker {position} moet een JSON-object zijn."
            )

        missing_fields = cls.REQUIRED_FIELDS - user_data.keys()

        if missing_fields:
            missing_fields_text = ", ".join(
                sorted(missing_fields)
            )

            raise IAMProvisioningError(
                f"Gebruiker {position} mist verplichte velden: "
                f"{missing_fields_text}."
            )

        username = cls._required_string(
            value=user_data["username"],
            field_name="username",
            position=position,
        )

        email = cls._required_string(
            value=user_data["email"],
            field_name="email",
            position=position,
        ).lower()

        role = cls._required_string(
            value=user_data["role"],
            field_name="role",
            position=position,
        ).lower()

        password = cls._optional_password(
            value=user_data.get("password"),
            position=position,
        )

        if role not in User.VALID_ROLES:
            valid_roles = ", ".join(
                sorted(User.VALID_ROLES)
            )

            raise IAMProvisioningError(
                f"Gebruiker {position} heeft een ongeldige rol. "
                f"Toegestane rollen: {valid_roles}."
            )

        return {
            "username": username,
            "email": email,
            "password": password,
            "role": role,
        }

    @staticmethod
    def _required_string(
        value: Any,
        field_name: str,
        position: int,
    ) -> str:
        """
        Controleer een verplicht tekstveld.
        """

        if not isinstance(value, str) or not value.strip():
            raise IAMProvisioningError(
                f"Het veld '{field_name}' van gebruiker {position} "
                "moet een tekstwaarde bevatten."
            )

        return value.strip()

    @staticmethod
    def _optional_password(
        value: Any,
        position: int,
    ) -> str | None:
        """
        Controleer een optioneel wachtwoord.

        Bij een bestaande gebruiker mag het wachtwoord ontbreken.
        In dat geval blijft het bestaande wachtwoord ongewijzigd.
        """

        if value is None:
            return None

        if not isinstance(value, str) or not value.strip():
            raise IAMProvisioningError(
                f"Het wachtwoord van gebruiker {position} "
                "mag niet leeg zijn."
            )

        return value.strip()

    @staticmethod
    def _find_user_by_email(
        email: str,
    ) -> User | None:
        """
        Zoek een bestaande gebruiker op e-mailadres.

        Het e-mailadres is binnen deze eenvoudige provisioningflow
        de identifier waarmee wordt bepaald of een gebruiker al bestaat.
        """

        return db.session.execute(
            db.select(User).where(
                User.email == email,
            )
        ).scalar_one_or_none()

    @staticmethod
    def _find_user_by_username(
        username: str,
    ) -> User | None:
        """
        Zoek een gebruiker op gebruikersnaam.

        Dit voorkomt dat een nieuwe of bijgewerkte gebruiker
        een gebruikersnaam van iemand anders overneemt.
        """

        return db.session.execute(
            db.select(User).where(
                User.username == username,
            )
        ).scalar_one_or_none()

    @classmethod
    def _create_user(
        cls,
        user_data: dict[str, str | None],
        position: int,
    ) -> None:
        """
        Maak een nieuwe gebruiker aan.
        """

        password = user_data["password"]

        if password is None:
            raise IAMProvisioningError(
                f"Gebruiker {position} is nieuw en heeft "
                "een wachtwoord nodig."
            )

        existing_username = cls._find_user_by_username(
            username=user_data["username"],
        )

        if existing_username is not None:
            raise IAMProvisioningError(
                f"De gebruikersnaam '{user_data['username']}' "
                f"van gebruiker {position} is al in gebruik."
            )

        # Jouw User-constructor roept set_password() aan.
        # Daardoor wordt het wachtwoord gehasht opgeslagen.
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=password,
            role=user_data["role"],
        )

        db.session.add(user)

    @classmethod
    def _update_user(
        cls,
        user: User,
        user_data: dict[str, str | None],
        position: int,
    ) -> None:
        """
        Werk een bestaande gebruiker bij.

        Wanneer geen wachtwoord is aangeleverd, blijft de bestaande
        password_hash ongewijzigd.
        """

        user_with_username = cls._find_user_by_username(
            username=user_data["username"],
        )

        if (
            user_with_username is not None
            and user_with_username.user_id != user.user_id
        ):
            raise IAMProvisioningError(
                f"De gebruikersnaam '{user_data['username']}' "
                f"van gebruiker {position} is al in gebruik."
            )

        user.username = user_data["username"]
        user.email = user_data["email"]
        user.role = user_data["role"]

        password = user_data["password"]

        if password is not None:
            # Gebruik de bestaande methode uit het User-model.
            # Sla nooit het leesbare wachtwoord rechtstreeks op.
            user.set_password(password)