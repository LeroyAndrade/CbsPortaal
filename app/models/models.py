from app.extensions.db import db

# === CBS Models (3e normaalvorm) ===
class CBSArticle(db.Model):
    __tablename__ = 'cbs_article'
    article_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    release_time = db.Column(db.DateTime)
    summary = db.Column(db.Text)
    url = db.Column(db.String(500))

class CbsRecord(db.Model):
    __tablename__ = 'cbs_records'
    id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String(100), nullable=False)
    raw_data = db.Column(db.JSON, nullable=False)
    fetched_at = db.Column(db.DateTime, nullable=False)