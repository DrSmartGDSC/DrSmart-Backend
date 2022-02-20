from cmath import log
from urllib import response
from flask import Flask, request, jsonify, abort
from models import init_db, SkinDisease
from auth import create_user, user_login, validate_access_token
from predict import predict_s, getSkinClasses
import os

app = Flask('SDD API')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)
getSkinClasses(app)




# check the access token
def authenticate():
    if 'Authorization' not in request.headers:
        abort(401, 'Missing the Authorization header')

    sp = request.headers['Authorization'].split(' ')
    if len(sp) != 2:
        abort(401, 'Invalid Authorization header')

    token = sp[1]
    payload = validate_access_token(token)

    if not payload:
        abort(401, 'Invalid access token')

    return payload


# endpoints


# predict

# skin
@app.post('/predict')
def predict_skin():
    authenticate()

    img = request.files.get('img')
    tp = request.form.get('type')

    print(tp)

    if img is None:
        abort(400, 'img is missing')
    if tp is None:
        abort(400, 'type is missing')

    try:
        tp = int(tp)
    except Exception:
        abort(400, f'invlaid type ({tp})')

    result = None
    if tp == 0: # skin
        result = predict_s(img)

    if result is None:
        abort(400, f"type ({tp}) doesn't exist")

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
        abort(400, 'fields missing')

    result = None
    if tp == 0: # skin
        try:
            result = SkinDisease.query.get(id).text
        except Exception as e:
            print(e)
            abort(500, "couldn't get the disease info")

    if result is None:
        abort(400, f"type {tp} does't exist")

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
        abort(400, "fields missing")

    if len(password) < 8:
        abort(422, 'A password can not be shorter than 8 characters')

    success, token = create_user({
        'email': email,
        'password': password,
        'full_name': full_name
    })
    if not success:
        abort(500, 'Failed to add the user. Make sure the email has not been used before')

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
        abort(400, "fields missing")

    success, token = user_login(email, password)
    if not success:
        abort(401, 'Invalid Credentials')

    return jsonify({
        'status': True,
        'email': email,
        'token': token,
    })


# index
@app.get('/')
def index():
    return 'The API is running'


# error handeling
@app.errorhandler(400)
def bad_request_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 400


@app.errorhandler(401)
def forbidden_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 401


@app.errorhandler(422)
def unprocessable_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 422


@app.errorhandler(500)
def server_error_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 500
