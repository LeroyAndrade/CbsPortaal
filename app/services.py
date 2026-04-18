import requests

CBS_URL = "https://www.cbs.nl/odata/v1/Articles?$top=1&$orderby=ReleaseTime desc"


def get_latest_cbs_article():
    response = requests.get(CBS_URL)
    response.raise_for_status()

    data = response.json()
    return data["value"][0]["Body"]