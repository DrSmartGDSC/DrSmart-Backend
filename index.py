from flask import Flask, request, jsonify, abort
from predict import predict
from models import init_db
from auth import create_user, user_login, validate_access_token
import os

app = Flask('SDD API')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)


# check the access token
def authenticate():
    if 'Authorization' not in request.headers:
        abort(403, 'Missing the Authorization header')

    sp = request.headers['Authorization'].split(' ')
    if len(sp) != 2:
        abort(403, 'Invalid Authorization header')

    token = sp[1]
    payload = validate_access_token(token)

    if not payload:
        abort(403, 'Invalid access token')

    return payload


# endpoints
# predict
@app.post('/predict')
def prediction():
	try:
		token = request.headers['Authorization'].split(' ')[1]
		payload = validate_access_token(token)
		if payload == False:
			raise Exception('invalid token')
	except Exception as e:
		print(str(e))
		abort(403, 'failed to validate the access token')

	img = request.files.get('img')
	result = predict(img)

	response = {
        'status': True,
        'data': {
            'result': result,
        },
    }

	return jsonify(response)


# signup
@app.post('/signup')
def signup():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    full_name = request.json.get('full_name', None)

    if None in [email, password, full_name]:
        abort(400, "fields missing")

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
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if None in [email, password]:
        abort(400, "fields missing")

    success, token = user_login(email, password)
    if not success:
        abort(403, 'Invalid Credentials')

    return jsonify({
        'status': True,
        'email': email,
        'token': token,
    })


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


@app.errorhandler(500)
def server_error_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 500


@app.errorhandler(403)
def forbidden_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 403
