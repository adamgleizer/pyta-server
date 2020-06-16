from pyta_server import db
from sqlalchemy.sql import func


class Devices(db.Model):
    """Represents unique devices sending data. Differentiated by version of PyTA used."""
    device_uuid = db.Column(db.String(800), primary_key=True)
    version = db.Column(db.String(800), nullable=False)
    uploads = db.relationship('Uploads', backref='device', lazy=True)


class Uploads(db.Model):
    """Represents an upload sent from PyTA. Records the time of upload, and configuration file used
    for any associated errors and files."""
    primary = db.Column(db.Integer, primary_key=True)
    upload_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    config = db.Column(db.String(800), nullable=True)
    device_id = db.Column(db.String(800), db.ForeignKey('devices.device_uuid'), nullable=False)
    files = db.relationship('Files', backref='upload', lazy=True)
    errors = db.relationship('Errors', backref='upload', lazy=True)


class Files(db.Model):
    """Represents a file checked and sent by PyTA"""
    primary = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.primary'), nullable=False)
    path = db.Column(db.String(800), nullable=False)
    errors = db.relationship('Errors', backref='file', lazy=True)


class Errors(db.Model):
    """Represents errors caught by PyTA. If files were uploaded along with the errors,
    then errors have a reference to the file at which they were caught."""
    primary = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('uploads.primary'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.primary'), nullable=True)
    msg_id = db.Column(db.String(800))
    msg = db.Column(db.String(800))
    symbol = db.Column(db.String(800))
    category = db.Column(db.String(800))
    line = db.Column(db.Integer)
