from pyta_server import db
from sqlalchemy.sql import func

class Submissions(db.Model):
    device_uuid = db.Column(db.String(200), server_default="no-id", primary_key=True)
    uploads = db.relationship('Uploads', backref='submission', lazy=True)
    version = db.Column(db.String(200), nullable=False)

class Uploads(db.Model):
    primary = db.Column(db.Integer, primary_key=True)
    upload_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    config = db.Column(db.String(200), nullable=True)
    submission_id = db.Column(db.String(200), db.ForeignKey('submissions.device_uuid'), nullable=False)

