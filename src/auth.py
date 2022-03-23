from time import time, timezone
import jwt
import os
from datetime import datetime, timezone, timedelta
from .models import db, User
import hashlib

ACCESS_SECRET = os.environ.get('ACCESS_SECRET')


def hashText(txt):
    return hashlib.sha256(txt.encode()).hexdigest()


def create_access_token(payload):
    payload['exp'] = datetime.now(tz=timezone.utc) + timedelta(days=30)

    token = jwt.encode(payload,  ACCESS_SECRET, algorithm='HS256')

    return token


def validate_access_token(token):
    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=["HS256"])
    except Exception as e:
        print(str(e))
        return False

    return payload


def create_user(user_data):
    try:

        user_data['password'] = hashText(user_data['password'])

        user = User(
            **user_data,
            created=datetime.now(tz=timezone.utc)
        )
        db.session.add(user)

        token = create_access_token({
            'email': user_data['email'],
            'user_id': user.id,
            'field_id': user.field_id,
            'is_doctor': user.is_doctor
        })

        u = dict()
        u['is_doctor'] = user.is_doctor
        u['field_id'] = user.field_id
        u['user_id'] = user.id
        u['name'] = user.full_name

        db.session.commit()
        return True, token, u
    except Exception as e:
        print(str(e))
        db.session.rollback()
        return False, '', None
    finally:
        db.session.close()


def user_login(email, password):
    try:
        user = User.query.filter(
            User.email == email,
            User.password == hashText(password)
        ).first()

        if user is None:
            raise Exception('user not found')

        u = dict()
        u['is_doctor'] = user.is_doctor
        u['field_id'] = user.field_id
        u['user_id'] = user.id
        u['name'] = user.full_name

        token = create_access_token({
            'email': email,
            'user_id': user.id,
            'field_id': user.field_id,
            'is_doctor': user.is_doctor
        })
        db.session.commit()

        return True, token, u
    except Exception as e:
        print(str(e))
        db.session.rollback()
        return False, '', None
    finally:
        db.session.close()
