import requests
from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from app.services.services import ArticleService

# Login
from app.models.user import User
from flask_login import login_user

bp = Blueprint('cbs', __name__)

@bp.route("/")
def index():
    return "hoofd pagina werkt."

@bp.route("/getArticles")
def getArticles():
    # url = "https://www.cbs.nl/odata/v1/Articles?waa$top=1&$orderby=ReleaseTime%20desc&select=Body"
    # url = "https://www.cbs.nl/odata/v1/Articles?$top=1&$orderby=ReleaseTime%20desc&$select=Body,Title,ReleaseTime,Url,Image"
    body_text = ArticleService.get_latest_cbs_article()
    return render_template('artikelen.html', articles=body_text)

    # return data

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            if user.check_password(password):
                session['logged_in'] = True
                session['user'] = username
                login_user(user)
                return redirect(url_for('bp.index'))
            else:
                flash('Login niet succesvol', 'error')
        else:
            flash('Login niet succesvol', 'error')

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Je bent uitgelogd', 'success')
    return redirect(url_for('main.index'))