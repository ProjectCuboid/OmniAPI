from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# ---------------- MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    projects = db.relationship('Project', backref='owner', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "key": self.key,
            "projects": [p.to_dict() for p in self.projects]
        }


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    short_url = db.Column(db.String(200), nullable=True)
    long_url = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "integrated_links": {
                "short_url": self.short_url,
                "long_url": self.long_url
            }
        }
