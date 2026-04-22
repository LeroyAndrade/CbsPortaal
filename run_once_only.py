import click


@click.command('create-admin')
def create_admin():
    from app.models.user import User
    from app.extensions.db import db

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password='admin2026',
            email='admin@cbsportaal.nl'
        )
        admin.set_password('admin2026')  # ensure hashing!
        db.session.add(admin)
        db.session.commit()