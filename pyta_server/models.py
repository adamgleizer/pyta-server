from pyta_server import db
from sqlalchemy.sql import func

class Submissions(db.Model):
    identifier = db.Column(db.String(200), server_default="no-id", primary_key=True)
    submit_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), primary_key=True)
    uploads = db.relationship('Uploads', backref='submission', lazy=True)
    config = db.Column(db.String(200), nullable=False)

class Uploads(db.Model):
    primary = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200), nullable=False)
    upload_time = db.Column(db.DateTime(timezone=True), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    __table_args__ = (db.ForeignKeyConstraint([user_id, upload_time],
                                           [Submissions.identifier, Submissions.submit_time]),
                      {})

