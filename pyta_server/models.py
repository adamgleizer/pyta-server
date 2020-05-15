from pyta_server import db
from sqlalchemy.sql import func

class Devices(db.Model):
    device_uuid = db.Column(db.String(800), server_default="no-id", primary_key=True)
    uploads = db.relationship('Uploads', backref='device', lazy=True)
    version = db.Column(db.String(800), nullable=False)

class Uploads(db.Model):
    primary = db.Column(db.Integer, primary_key=True)
    upload_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = db.Column(db.String(800), nullable=False)
    config = db.Column(db.String(800), nullable=True)
    device_id = db.Column(db.String(800), db.ForeignKey('devices.device_uuid'), nullable=False)

