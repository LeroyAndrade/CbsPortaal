import requests

class ArticleService:
    
    @staticmethod
    def get_latest_cbs_article():
        url = "https://www.cbs.nl/odata/v1/Articles?$top=3&$orderby=ReleaseTime%20desc&$select=Title,Url,Image"

        try:
            r = requests.get(url)
            data = r.json()
            body_text = data["value"]
            return body_text
        except Exception as e:
            print(f"Artikelen fetchen error: \n{e}")
            return []