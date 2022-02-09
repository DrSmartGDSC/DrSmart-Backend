from time import timezone
import jwt
import os
from datetime import datetime, timezone

ACCESS_SECRET = os.environ.get('ACCESS_SECRET')

def create_access_token(payload):
    payload['exp'] = datetime.now(tz=timezone.utc)
    
    token = jwt.encode(payload,  ACCESS_SECRET, algorithm='HS256')
    

    return token

def verify_access_token(token):
    try:
        payload = jwt.decode(token, ACCESS_SECRET, algorithms=["HS256"])
    except Exception as e:
        print(str(e))
        return False

    return payload