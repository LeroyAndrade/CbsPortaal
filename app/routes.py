import requests
from flask import Blueprint, render_template, request, session, flash, redirect, url_for

main = Blueprint('main', __name__)

@main.route("/")
def index():
    return "hoofd pagina werkt"

@main.route("/getArticles")
def getArticles():
    # url = "https://www.cbs.nl/odata/v1/Articles?waa$top=1&$orderby=ReleaseTime%20desc&select=Body"
    # url = "https://www.cbs.nl/odata/v1/Articles?$top=1&$orderby=ReleaseTime%20desc&$select=Body,Title,ReleaseTime,Url,Image"
    url = "https://www.cbs.nl/odata/v1/Articles?$top=3&$orderby=ReleaseTime%20desc&$select=Title,Url,Image"
    r = requests.get(url)
    data = r.json()
    body_text = data["value"]
    return render_template('artikelen.html', articles=body_text)

    # return data

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # tijdelijke check, to do (later vervangen door echte db check)
        if username == "admin" and password == "admin123":
            session['user'] = username
            flash('Je bent ingelogd', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Verkeerde login', 'error')

    return render_template('login.html')


@main.route('/logout')
def logout():
    session.pop('user', None)
    flash('Je bent uitgelogd', 'success')
    return redirect(url_for('main.index'))