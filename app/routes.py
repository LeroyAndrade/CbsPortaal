# Flask imports
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from datetime import datetime, UTC
import logging
# Flask-Login imports
from flask_login import logout_user, login_user, login_required, current_user
from typing import List

# Eigen imports
from app.services.services import ArticleService, DatasetDropdownService, CbsDataService, UserLog
from app.models.user import User, UserLogging
from app.extensions.db import db

bp = Blueprint('cbs', __name__)

@bp.route("/")
def index():
    return redirect(url_for('cbs.articles'))



@bp.route("/articles")
@login_required
def articles():
    body_text = ArticleService.get_latest_cbs_article()
    body_dropdown = DatasetDropdownService.get_datasets()
# Debug info -delete me
    logging.debug(body_text)
    return render_template('artikelen.html', articles=body_text, dropdown=body_dropdown, current_user=current_user.username)



@bp.route("/cbs/data")
def cbs_data():
    dataset = request.args.get("dataset")

    if not dataset:
        return jsonify({"error": "Geen dataset meegegeven"}), 400

    valid_datasets = DatasetDropdownService.get_datasets()

    if dataset not in valid_datasets:
        return jsonify({"error": "Ongeldige dataset"}), 400

    data = CbsDataService.get_data(dataset)

    return jsonify(data)



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()

        # als je al bent ingelogd en opnieuw inlogt via het formulier, ga naar homepagina
        if current_user.is_authenticated:
            return redirect(url_for('cbs.index'))

        if user:
            if user.check_password(password):
                # logging
                UserLog.log_action(user, "Ingelogd")
                session['logged_in'] = True
                session['user'] = username

                # todo, ook deze tijd van de server halen
                user.last_logged_in = datetime.now(UTC)
                db.session.commit()

                login_user(user)
                return redirect(url_for('cbs.articles'))
            else:
                flash('Login niet succesvol', 'error')
        else:
            flash('Login niet succesvol', 'error')

        # als je al bent ingelogd en willekeurig naar de pagina toe gaat
        if current_user.is_authenticated:
            return redirect(url_for('cbs.index'))

    return render_template('login.html')


@bp.route('/test')
def test():
    return render_template('test.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Gebruikersnaam bestaat al', 'error')
            # todo add: IP
            UserLog.log_action(user, "Registratie poging door een ander")
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()

    # UserLog.log_action(user, "Registratie succesvol")

            flash('Account aangemaakt, u kunt nu inloggen', 'success')
            return redirect(url_for('cbs.login'))

    return render_template('register.html')


@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
       UserLog.log_action(current_user, "Logged out")

    # session['_user_id'] = False
    logout_user()
    session.pop('user', None)
    flash('U bent uitgelogd', 'success')
    return redirect(url_for('cbs.login'))