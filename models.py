from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(30), nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    def __str__(self) -> str:
        return f"Patient: email:{self.email}"

    def __repr__(self) -> str:
        return f"Patient: email:{self.email}"

class SkinDisease(db.Model):
    __tablename__ = 'skin_diseases'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    text = db.Column(db.String(1400), nullable=False)

    def __str__(self) -> str:
        return f"Skin Disease: name:{self.name} id:{self.id}"

    def __repr__(self) -> str:
        return f"Skin Disease: name:{self.name} id:{self.id}"


class LungDisease(db.Model):
    __tablename__ = 'lung_diseases'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    text = db.Column(db.String(1400), nullable=False)

    def __str__(self) -> str:
        return f"Lung Disease: name:{self.name} id:{self.id}"

    def __repr__(self) -> str:
        return f"Lung Disease: name:{self.name} id:{self.id}"



def init_db(app):
    db.init_app(app)
    Migrate(app, db)
    with app.app_context():
        db.create_all()
