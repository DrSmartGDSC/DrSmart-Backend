from time import time, timezone
import jwt
import os
from datetime import datetime, timezone, timedelta
from models import db, User

ACCESS_SECRET = os.environ.get('ACCESS_SECRET')


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
        db.session.add(User(
            **user_data,
            created=datetime.now(tz=timezone.utc)
        ))
        token = create_access_token({'email': user_data['email']})

        db.session.commit()
        return True, token
    except Exception as e:
        print(str(e))
        db.session.rollback()
        return False, ''
    finally:
        db.session.close()


def user_login(email, password):
    try:
        user = User.query.filter(
            User.email == email,
            User.password == password
        ).first()

        if user is None:
            raise Exception('user not found')

        token = create_access_token({'email': email})
        db.session.commit()

        return True, token
    except Exception as e:
        print(str(e))
        db.session.rollback()
        return False, ''
    finally:
        db.session.close()
