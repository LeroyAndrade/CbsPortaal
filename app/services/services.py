import httpx
import requests

class ArticleService:

    @staticmethod
    def get_latest_cbs_article():
        # url = "https://www.cbs.nl/odata/v1/Articles?$filter=endswith(UniqueId, '-nl-nl')&$skip=3&$top=6&$orderby=ReleaseTime%20desc&$select=Title,Url,Image,Themes,TaxonomyTags,LeadText"
        url = "https://www.cbs.nl/odata/v1/Articles?$filter=Language eq 'nl-NL'&$skip=2&$top=3&$orderby=ReleaseTime%20desc&$select=Title,Url,Image,Themes,TaxonomyTags,LeadText"

        try:
            with httpx.Client() as client:
                r = client.get(url)
                r.raise_for_status()
                data = r.json()
                return data.get("value", [])
        except Exception as e:
            print(f"Artikelen fetchen error: \n{e}")
            return []

class CbsDatasetDropdownService:
    BASE_URL = "https://www.cbs.nl/odata/v1/Articles?$filter=Language eq 'nl-NL'&"

    import httpx
    class CbsDatasetDropdownService:
        BASE_URL = "https://www.cbs.nl/odata/v1/"

        @staticmethod
        def get_datasets():
            try:
                with httpx.Client(timeout=10) as client:
                    response = client.get(CbsDatasetDropdownService.BASE_URL)
                    response.raise_for_status()
                    data = response.json()

                    datasets = [item["name"] for item in data.get("value", [])]
                    return datasets

            except Exception:
                return ["Articles", "Vacancies", "Pages"]

