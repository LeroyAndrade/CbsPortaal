# Flask imports
from flask import Blueprint, render_template, request, session, flash, redirect, url_for

# Flask-Login imports
from flask_login import logout_user, login_user, login_required, current_user

# Eigen imports
from app.services.services import ArticleService
from app.models.user import User
from app.extensions.db import db

bp = Blueprint('cbs', __name__)

@bp.route("/")
def index():
    return "hoofd pagina werkt."

@bp.route("/getArticles")
@login_required
def getArticles():
    # url = "https://www.cbs.nl/odata/v1/Articles?waa$top=1&$orderby=ReleaseTime%20desc&select=Body"
    # url = "https://www.cbs.nl/odata/v1/Articles?$top=1&$orderby=ReleaseTime%20desc&$select=Body,Title,ReleaseTime,Url,Image"
    body_text = ArticleService.get_latest_cbs_article()
    return render_template('artikelen.html', articles=body_text)

    # return data

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()

        # als je al bent ingelogd ga naar homepagina
        if current_user.is_authenticated:
            return redirect(url_for('cbs.index'))

        if user:
            if user.check_password(password):
                session['logged_in'] = True
                session['user'] = username
                login_user(user)
                return redirect(url_for('artikelen.html'))
            else:
                flash('Login niet succesvol', 'error')
        else:
            flash('Login niet succesvol', 'error')

    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Gebruikersnaam bestaat al', 'error')
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account aangemaakt, je kunt nu inloggen', 'success')
            return redirect(url_for('cbs.login'))

    return render_template('register.html')
@bp.route('/logout')
def logout():
    session['logged_in'] = False
    logout_user()
    session.pop('user', None)
    flash('U bent uitgelogd', 'success')
    return redirect(url_for('/'))