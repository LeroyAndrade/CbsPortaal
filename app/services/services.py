import logging

import httpx

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
        url = BASE_URL+"/Articles?$filter=Language eq 'nl-NL'&$skip=2&$top=3&$orderby=ReleaseTime%20desc&$select=Title,Url,Image,Themes,TaxonomyTags,LeadText"

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