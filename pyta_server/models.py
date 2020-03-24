from pyta_server import db
from sqlalchemy.sql import func

class Uploads(db.Model):
    primary = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(200), nullable=False)
    config = db.Column(db.String(200), nullable=False)
    identifier = db.Column(db.String(200), server_default="no-id", nullable=False)
    upload_time = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Uploads(source={self.source}, config={self.config})>"
