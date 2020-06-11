from pyta_server import db
from sqlalchemy.sql import func


class Devices(db.Model):
    device_uuid = db.Column(db.String(800), primary_key=True)
    version = db.Column(db.String(800), nullable=False)
    uploads = db.relationship('Uploads', backref='device', lazy=True)


class Uploads(db.Model):
    device_id = db.Column(db.String(800), db.ForeignKey('devices.device_uuid'), nullable=False)
    primary = db.Column(db.Integer, primary_key=True)
    upload_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = db.Column(db.String(800), nullable=False)
    config = db.Column(db.String(800), nullable=True)
    errors = db.relationship('Errors', backref='file', lazy=True)


class Errors(db.Model):
    primary = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploads.primary'), nullable=True)
    msg_id = db.Column(db.String(800))
    msg = db.Column(db.String(800))
    symbol = db.Column(db.String(800))
    category = db.Column(db.String(800))
    line = db.Column(db.Integer)
