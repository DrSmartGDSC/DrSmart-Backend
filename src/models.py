from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(30), nullable=False)
    is_doctor = db.Column(db.Boolean, default=False)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'))
    created = db.Column(db.DateTime, nullable=False)

    field = db.relationship('Field')

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


class Field(db.Model):
    __tablename__ = 'fields'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    desc = db.Column(db.String(1024))
    img = db.Column(db.Text)  # base64
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('fields.id'), nullable=False)

    user = db.relationship('User')
    field = db.relationship('Field')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1024))
    img = db.Column(db.Text)  # base64
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    post = db.relationship('Post')
    user = db.relationship('User')


def init_db(app):
    db.init_app(app)
    Migrate(app, db)
    with app.app_context():
        db.create_all()
