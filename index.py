from cmath import log
from urllib import response
from flask import Flask, request, jsonify
from models import init_db, SkinDisease
from auth import create_user, user_login, validate_access_token
from predict import predict_s, getSkinClasses
import os

app = Flask('SDD API')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)
getSkinClasses(app)




def err(msg):
    return jsonify({
        'status': False,
        'error': msg
    })

# check the access token
def authenticate():
    if 'Authorization' not in request.headers:
        return err('Missing the Authorization header')

    sp = request.headers['Authorization'].split(' ')
    if len(sp) != 2:
        return err('Invalid Authorization header')

    token = sp[1]
    payload = validate_access_token(token)

    if not payload:
        return err('Invalid access token')

    return payload


# endpoints


# predict

# skin
@app.post('/predict')
def predict_skin():
    authenticate()

    img = request.files.get('img')
    tp = request.form.get('type')

    if img is None:
        return err('img is missing')
    if tp is None:
        return err('type is missing')

    try:
        tp = int(tp)
    except Exception:
        return err(f'invalid type ({tp})')

    result = None
    if tp == 0: # skin
        result = predict_s(img)
        result = list(filter(lambda x: round(x['confidence']) > 0, result))

    if result is None:
        return err(f"type ({tp}) doesn't exist")

    response = {
        'status': True,
        'data': {
            'result': result,
        },
    }

    return jsonify(response)


@app.get('/info')
def info():
    authenticate()
    id = request.form.get('id')
    tp = request.form.get('type')

    if None in [id, tp]:
        return err('fields missing')

    result = None
    if tp == 0: # skin
        try:
            result = SkinDisease.query.get(id).text
        except Exception as e:
            print(e)
            return err(500, "couldn't get the disease info")

    if result is None:
        return err(f"type {tp} does't exist")

    response = {
        'status': True,
        'data': {
            'result': result,
        }
    }

    return jsonify(response)



## signup and login

# signup
@app.post('/signup')
def signup():
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    full_name = request.form.get('full_name', None)

    if None in [email, password, full_name]:
        return err("fields missing")

    if len(password) < 8:
        return err('A password can not be shorter than 8 characters')

    success, token = create_user({
        'email': email,
        'password': password,
        'full_name': full_name
    })
    if not success:
        return err('Failed to add the user. Make sure the email has not been used before')

    return jsonify({
        'status': True,
        'email': email,
        'token': token,
    })

# login


@app.post('/login')
def login():
    email = request.form.get('email', None)
    password = request.form.get('password', None)

    if None in [email, password]:
        return err("fields missing")

    success, token = user_login(email, password)
    if not success:
        return err('Invalid Credentials')

    return jsonify({
        'status': True,
        'email': email,
        'token': token,
    })


# index
@app.get('/')
def index():
    return 'The API is running'

@app.errorhandler(500)
def server_error_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 500
