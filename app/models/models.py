from app.extensions.db import db

# === CBS Models (3e normaalvorm) ===
class CBSArticle(db.Model):
    __tablename__ = 'cbs_article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    release_time = db.Column(db.DateTime)
    summary = db.Column(db.Text)
    url = db.Column(db.String(500))

class CBSEvent(db.Model):
    __tablename__ = 'cbs_event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))