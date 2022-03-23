# DR.Smart Backend API
This is the backend of the Dr.Smart app. The API processes images for diagnoses and manges the database.

# Install
1. First there are some environemt vaiables you need. you will find them in `.env.template.txt`
2. Install the requirements
```
pip install -r requirements.txt
```
3. Now you can run it
```
python run.py
```

If you added the `SKIN_MODEL_ID`, and `LUNG_MODEL_ID` env vars, the models will get downloaded, then the app will start. If you didn't add them, and didn't download the models, then the app will probably crash.

The `SKIN_MODEL_ID`, and the `LUNG_MODEL_ID` are the IDs of the tensorflow models on Google Drive.

# Endpoints
The endpoints receive data as FormData and respondes on JSON.

## `/signup [POST]`

### Request
```
email : string
password : string
full_name : string
is_doctor : int
field_id : int
```

### Response
```json
{
    "status": true,
    "email": "email",
    "token": "token",
    "user": {
        "is_doctor": true,
        "field_id": 1,
        "name": "name"
    }
}
```

## `/login [POST]`

### Request
```
email : string
password : string
```

### Response
```json
{
    "status": true,
    "email": "email",
    "token": "token",
    "user": {
        "is_doctor": true,
        "field_id": 1,
        "name": "name"
    }
}
```

## `/fields [GET]`

### Response
```json
{
    "status": true,
    "data": {
        "fields": [
            {
                "id": 1,
                "name": "Nursing"
            }
        ]
    }
}
```

## `/Info [GET]`
#### `Authentication Required`

### URL Args
```
id : int (id of the disease)
type : int (0 == skin, 1 == lung)
```

### Response
```json
{
    "status": true,
    "data": {
        "fields": [
            {
                "id": 1,
                "name": "Nursing"
            }
        ]
    }
}
```

## `/predict [POST]`
#### `Authentication Required`

### Request
```
img : image file
type : int (0 == sking, 1 == lung)
```

### Response
```json
{
    "data": {
        "result": [
            {
                "confidence": 99.99731779098511,
                "id": 3,
                "name": "virus"
            }
        ]
    },
    "status": true
}
```

## `/posts [GET]`
#### `Authentication Required`

### optional URL Args
```
limit : int (default = 10)
page : int (default = 1)
```

### Response
```json
{
    "status": true,
    "data": {
        "posts": [
            {
                "answered": false,
                "desc": "some desc",
                "field": "Nursing",
                "img": null,
                "post_id": 19,
                "user_name": "some user"
            }
        ]
    }
}
```

## `/posts/<id> [GET]`
#### `Authentication Required`


### Response
```json
{
    "status": true,
    "data": {
        "post": 
            {
                "answered": false,
                "desc": "some desc",
                "field": "Nursing",
                "img": null,
                "post_id": 19,
                "user_name": "some user"
            }
        
    }
}
```

## `/posts/<id>/comments [GET]`
#### `Authentication Required`

### optional URL Args
```
limit : int (default = 10)
page : int (default = 1)
```

### Response
```json
{
    "status": true,
    "data": {
        "comments": [
            {
                "comment_id": 18,
                "img": null,
                "text": "jgjh",
                "user_id": 18,
                "user_name": "test user"
            },
        ]   
    }
}
```

## `/posts [POST]`
#### `Authentication Required`

### Request
```
desc: string
field_id: int
img: image file (optional)
```

### Response
```json
{
    "status": true,
    "post_id": 6
}
```

## `/posts/<post_id>/comments [POST]`
#### `Authentication Required`

### Request
```
text: string
img: image file (optional)
```

### Response
```json
{
    "status": true,
    "comment_id": 15
}
```

## `/posts/<post_id>/end [POST]`
#### `Authentication Required`

### Response
```json
{
    "status": true,
    "post_id": 6
}
```