from flask import Flask, request, jsonify
from predict import predict

app = Flask('SDD API')


# endpoints
@app.post('/predict')
def prediction():
	img = request.files.get('img')
	result = predict(img)

	response = {
		'result': result
	}

	return jsonify(response)

@app.get('/')
def index():
	return 'The API is running'
