from flask import request, jsonify
from predict import predict
from models import app


# endpoints
@app.post('/predict')
def prediction():
    img = request.files.get('img')
    result = predict(img)

    response = {
        'status': True,
        'data': {
            'result': result,
        },
    }

    return jsonify(response)


@app.get('/')
def index():
    return 'The API is running'
