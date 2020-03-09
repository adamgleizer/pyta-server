from pyta_server import db

class Uploads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(200), nullable=False)
    config = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Uploads(source={self.source}, config={self.config})>"
