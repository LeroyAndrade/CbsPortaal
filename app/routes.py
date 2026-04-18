import requests
from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route("/getArticles")
def getArticles():
    # url = "https://www.cbs.nl/odata/v1/Articles?$top=1&$orderby=ReleaseTime%20desc&select=Body"
    # url = "https://www.cbs.nl/odata/v1/Articles?$top=1&$orderby=ReleaseTime%20desc&$select=Body,Title,ReleaseTime,Url,Image"
    url = "https://www.cbs.nl/odata/v1/Articles?$top=3&$orderby=ReleaseTime%20desc&$select=Title,Url,Image"
    r = requests.get(url)
    data = r.json()
    body_text = data["value"]
    return render_template('artikelen.html', articles=body_text)

    # return data

@main.route("/")
def getMainPage():
    return "hoofd pagina werkt"