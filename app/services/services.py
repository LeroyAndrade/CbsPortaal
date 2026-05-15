import logging

import httpx
from datetime import datetime, UTC
from app.extensions.db import db

from app.models.user import UserLogging, User, CBSArticle

# Debug info
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(message)s"
)

BASE_URL = "https://www.cbs.nl/odata/v1"

class ArticleService:

    @staticmethod
    def get_latest_cbs_article():
        # url = "https://www.cbs.nl/odata/v1/Articles?$filter=endswith(UniqueId, '-nl-nl')&$skip=3&$top=6&$orderby=ReleaseTime%20desc&$select=Title,Url,Image,Themes,TaxonomyTags,LeadText"
        url = BASE_URL+"/Articles?$filter=Language eq 'nl-NL'&$skip=1&$top=6&$orderby=ReleaseTime%20desc&$select=Title,Url,Image,Themes,TaxonomyTags,LeadText"

        try:
            with httpx.Client() as client:
                r = client.get(url)
                r.raise_for_status()
                data = r.json()
# Debug info
                logging.debug(f"data: {data}")
                logging.debug(f"data keys: {data.keys()}")
                logging.debug(f"value: {data.get('value')}")
                return data.get("value", [])

        except Exception as e:
            print(f"Artikelen fetchen error: \n{e}")
            return []



class DatasetDropdownService:
    @staticmethod
    def get_datasets():
        # maak een lege lijst voor aankomende loop
        datasets = []
        try:
             with httpx.Client(timeout=10) as client:
                response = client.get(BASE_URL)
                response.raise_for_status()

                data = response.json()

                # loop door alles wat CBS teruggeeft in de API
                for item in data.get("value", []):
                    datasets.append(item["name"])
# Debug info
                logging.info(f"CBS datasets opgehaald: {datasets}")
                return datasets

        except Exception as e:
            logging.error(f"Fout bij ophalen CBS datasets: {e}")
            return datasets




class CbsDataService:

    @staticmethod
    def get_data(dataset):
        try:
            # http://localhost:5000/cbs/data?dataset=Articles
            # https://www.cbs.nl/odata/v1    /Articles
            url = f"{BASE_URL}/{dataset}"

            with httpx.Client(timeout=10) as client:
                response = client.get(url)
                response.raise_for_status()

                data = response.json()

                return data.get("value", [])

        except Exception as e:
            logging.error(f"Fout bij ophalen CBS data: {e}")
            return []



# Logging user acties
class UserLog:

    @staticmethod
    def log_action(user: User | None, actie: str, logged_at: datetime | None = None):

        if logged_at is None:
            logged_at = datetime.now(UTC)

        if user is None:
            logging.warning(f"Geen user gevonden voor log: {actie}")
            return

        if hasattr(user, "logs") != True:
            logging.warning(f"User heeft geen logs relatie: {actie}")
            return

        log_entry = UserLogging(useracties=actie, logged_at=logged_at)

        user.logs.append(log_entry)

        db.session.add(log_entry)
        db.session.commit()
        db.session.flush()



class SlaArtikelOp:
    def save_10_artikelen(self, articles_list):
        """Slaat maximaal 10 artikelen op uit een lijst"""
        if not articles_list:
            print("Geen artikelen ontvangen")
            return

        added = 0
        for record in articles_list[:10]:
            article = CBSArticle(
                title=record.get('Title', 'Geen titel'),
                release_time=record.get('ReleaseTime'),
                summary=record.get('MetaDescription', ''),
                url=record.get('Url', ''),
                fetched_at=datetime.utcnow()
            )

            # Simpele duplicate check
            existing = CBSArticle.query.filter_by(
                title=article.title,
                release_time=article.release_time
            ).first()

            if existing:
                print(f"SKIP: {article.title[:60]}")
                continue

            db.session.add(article)
            added += 1
            print(f"TOEVOEGEN: {article.title[:60]}")

        if added > 0:
            db.session.commit()
            print(f"SUCCES → {added} artikelen opgeslagen")
        else:
            print("Niets nieuws om op te slaan")


class OnlineUsers:
    @staticmethod
    def get_online_users():
        loggedin = User.query.all()
        return loggedin
