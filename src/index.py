from flask import Flask, request, jsonify, abort
from .models import *
from .auth import create_user, user_login, validate_access_token
from .predict import predict_s, getSkinClasses, predict_l, getLungClasses
import os
import base64
from google.cloud import storage
from datetime import datetime

# Config
app = Flask('SDD API')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db(app)
getSkinClasses(app)
getLungClasses(app)


CLOUD_STORAGE_BUCKET = os.environ.get("CLOUD_STORAGE_BUCKET")
with app.app_context():
    FIELDS = list(
        map(lambda x: {'name': x.name, 'id': x.id}, Field.query.all()))


# check the access token
def authenticate():
    if 'Authorization' not in request.headers:
        return abort(400, 'Missing the Authorization header')

    sp = request.headers['Authorization'].split(' ')
    if len(sp) != 2:
        return abort(401, 'Invalid Authorization header')

    token = sp[1] # the token side
    payload = validate_access_token(token) # False if invalid

    if not payload:
        return abort(401, 'Invalid access token')

    return payload


## Endpoints ##


# skin
@app.post('/predict')
def predict_skin():
    authenticate()

    # taking input
    img = request.files.get('img')
    tp = request.form.get('type')

    # validation
    if img is None:
        return abort(400, 'img is missing')
    if tp is None:
        return abort(400, 'type is missing')

    try:
        tp = int(tp)
    except Exception:
        return abort(400, f'invalid type ({tp})')
    
    # sanning the the image
    result = None
    if tp == 0:  # skin
        result = predict_s(img)
        result = list(filter(lambda x: round(x['confidence']) > 0, result))

    if tp == 1:  # lung
        result = predict_l(img)
        result = list(filter(lambda x: round(x['confidence']) > 0, result))

    if result is None:
        return abort(400, f"type ({tp}) doesn't exist")

    response = {
        'status': True,
        'data': {
            'result': result,
        },
    }

    return jsonify(response)

# info about each disease
@app.get('/info')
def info():
    authenticate()

    # input
    id = request.args.get('id')
    tp = request.args.get('type')

    # validate
    if None in [id, tp]:
        return abort(400, 'fields missing')

    try:
        id = int(id)
        tp = int(tp)
    except Exception as e:
        print(e)
        return abort(400, 'Invalid id or type.')

    # get the info
    result = None
    if tp == 0:  # skin
        try:
            result = SkinDisease.query.get(id).text
        except Exception as e:
            print(e)
            return abort(500, "couldn't get the disease info")

    if tp == 1:  # lung
        try:
            result = LungDisease.query.get(id).text
        except Exception as e:
            print(e)
            return abort(500, "couldn't get the disease info")

    if result is None:
        return abort(400, f"type {tp} does't exist")

    response = {
        'status': True,
        'data': {
            'result': result,
        }
    }

    return jsonify(response)


## SIGNUP AND LOGIN ##


# signup
@app.post('/signup')
def signup():
    # input
    email = request.form.get('email', None)
    password = request.form.get('password', None)
    full_name = request.form.get('full_name', None)

    is_doctor = request.form.get('is_doctor', 0)
    is_doctor = is_doctor == '1'  # 1 == true, 0 == false

    field_id = request.form.get('field_id', None)

    # validate
    if None in [email, password, full_name]:
        return abort(400, "fields missing")

    if is_doctor and field_id is None:
        return abort(400, 'A doctor without a field')

    if is_doctor:
        try:
            field_id = int(field_id)
        except Exception:
            return abort(400, 'Invalid field id')

    if len(password) < 8:
        return abort(400, 'A password can not be shorter than 8 characters')


    # create the user
    if is_doctor:
        success, token, user = create_user({
            'email': email,
            'password': password,
            'full_name': full_name,
            'is_doctor': is_doctor,
            "field_id": field_id
        })
    else:
        success, token, user = create_user({
            'email': email,
            'password': password,
            'full_name': full_name
        })

    if not success:
        return abort(409, 'Failed to add the user. Make sure the email has not been used before')

    return jsonify({
        'status': True,
        'email': email,
        'token': token,
        'user': user
    })

# login
@app.post('/login')
def login():
    # input
    email = request.form.get('email', None)
    password = request.form.get('password', None)

    # validate
    if None in [email, password]:
        return avort(400, "fields missing")

    # login
    success, token, user = user_login(email, password)
    if not success:
        return abort(401, 'Invalid Credentials')

    return jsonify({
        'status': True,
        'email': email,
        'token': token,
        'user': user
    })



# get fields
@app.get('/fields')
def get_fields():
    return {
        'status': True,
        'data': {
            'fields': FIELDS
        }
    }



## POSTS ##


# create a post
@app.post('/posts')
def create_post():
    payload = authenticate()
    # input
    user_id = payload['user_id']

    desc = request.form.get('desc')
    field_id = request.form.get('field_id')
    img = request.files.get('img')

    # validate
    if None in [desc, field_id]:
        abort(400, 'fields missing')

    try:
        field_id = int(field_id)
    except Exception:
        abort(400, 'field_id must be an integer')

    if field_id < 1 or field_id > 29:
        abort(400, 'field_id must be between 1 and 29')

    # store the image on Google Storage
    img_url = None
    if img:
        # Create a Cloud Storage client.
        storage_client = storage.Client()

        # Get the bucket that the file will be uploaded to.
        bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

        # Create a new blob and upload the file's content.
        blob = bucket.blob(
            str(user_id) + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + img.filename)
        blob.upload_from_string(img.read(), content_type=img.content_type)

        # Make the blob publicly viewable.
        blob.make_public()

        img_url = blob.public_url

    # create the post
    try:
        post = Post(
            desc=desc,
            field_id=field_id,
            user_id=user_id,
            img=img_url
        )
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        print(str(e))
        db.session.rollback()
        abort(500, 'failed to create the post')

    return {
        'status': True,
        'post_id': post.id
    }


# get posts
@app.get('/posts')
def get_posts():
    payload = authenticate()

    # input
    is_doctor = payload['is_doctor']
    field_id = payload['field_id']
    user_id = payload['user_id']

    # validate
    try:
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
    except:
        abort(400, 'make sure you are passing int')

    # get the posts
    if is_doctor:
        posts = Post.query.order_by(Post.id.desc()).filter(
            Post.field_id == field_id, Post.answered == False).paginate(page, limit, error_out=False)
    else:
        posts = Post.query.order_by(Post.id.desc()).filter(
            Post.user_id == user_id).paginate(page, limit, error_out=False)

    # turn the posts into a list of dictionaries
    posts = list(
        map(lambda x: {
            'post_id': x.id,
            'desc': x.desc,
            'field': x.field.name,
            'answered': x.answered,
            'img': x.img,
            'user_name': x.user.full_name,
            'user_id': x.user.id
        }, posts.items))

    return {
        'status': True,
        'data': {
            'posts': posts
        }
    }



# get a single post
@app.get('/posts/<post_id>')
def get_post(post_id):
    authenticate()

    # input
    try:
        post_id = int(post_id)
        post = Post.query.get(post_id)
        if post is None:
            raise Exception('post not found')
    except Exception as e:
        print(str(e))
        abort(404, 'post not found')

    # return the post info
    return {
        'status': True,
        'data': {
            'post': {
                'desc': post.desc,
                'img': post.img,
                'user_id': post.user_id,
                'field_id': post.field_id,
                'field': post.field.name,
                'user_name': post.user.full_name
            }
        }
    }



# create a comment
@app.post('/posts/<post_id>/comments')
def create_comment(post_id):
    payload = authenticate()
    
    # input
    user_id = payload['user_id']

    text = request.form.get('text')
    img = request.files.get('img')

    # validate
    if None in [text, post_id]:
        abort(400, 'fields missing')

    try:
        post_id = int(post_id)
    except Exception:
        abort(400, 'post_id must be an integer')

    # store the image on Google Storage
    img_url = None
    if img:
        # Create a Cloud Storage client.
        storage_client = storage.Client()

        # Get the bucket that the file will be uploaded to.
        bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

        # Create a new blob and upload the file's content.
        blob = bucket.blob(
            str(user_id) + datetime.today().strftime('%Y-%m-%d-%H:%M:%S') + img.filename)
        blob.upload_from_string(img.read(), content_type=img.content_type)

        # Make the blob publicly viewable.
        blob.make_public()

        img_url = blob.public_url

    # create the comment
    try:
        comment = Comment(
            text=text,
            post_id=post_id,
            user_id=user_id,
            img=img_url
        )
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        print(str(e))
        db.session.rollback()
        abort(500, 'failed to create the comment')

    return {
        'status': True,
        'comment_id': comment.id
    }



# get the comments of a post
@app.get('/posts/<post_id>/comments')
def get_comments(post_id):
    payload = authenticate()

    # input
    try:
        limit = int(request.form.get('limit', 10))
        page = int(request.form.get('page', 1))
    except:
        abort(400, 'make sure you are passing int')

    try:
        post_id = int(post_id)
    except Exception:
        abort(400, 'post_id must be an integer')

    # get the comments
    comments = Comment.query.order_by(Comment.id.desc()).filter(
        Comment.post_id == post_id).paginate(page, limit, error_out=False)

    # turn into dictionaries
    comments = list(
        map(lambda x: {
            'text': x.text,
            'img': x.img,
            'user_id': x.user_id,
            'comment_id': x.id,
            'user_name': x.user.full_name
        }, comments.items))

    return {
        'status': True,
        'data': {
            'comments': comments
        }
    }


# close a post (got an answer)
# they all return 200
@app.post('/posts/<post_id>/end')
def end_post(post_id):
    authenticate()

    # input
    try:
        post_id = int(post_id)
        post = Post.query.get(post_id)
        if post is None:
            raise Exception('post not found')
    except Exception as e:
        print(str(e))
        abort(404, 'post not found')

    # mark the post as answered
    try:
        post.answered = True
        db.session.commit()
    except:
        db.session.rollback()
        abort(500, 'some error happened')

    return {
        'status': True,
        'post_id': post.id
    }


# just to check if the api is running
@app.get('/')
def index():
    return 'The API is running'



# error handelers
@app.errorhandler(400)
def bad_request_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 200


@app.errorhandler(401)
def forbidden_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 200


@app.errorhandler(404)
def forbidden_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 200


@app.errorhandler(409)
def forbidden_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 200


@app.errorhandler(422)
def unprocessable_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 200


@app.errorhandler(500)
def server_error_handeler(error):
    return jsonify({
        'status': False,
        'error': error.description
    }), 200
