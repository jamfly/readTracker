import hashlib
import random
from io import BytesIO
from pymongo import MongoClient
from flask import Flask, request, Response, send_file
from PIL import Image


app = Flask(__name__)
mongoClient = MongoClient('localhost')
db = mongoClient['mail_database']
collection = db['mail_collection']


def generate_salt():
    ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    salt = ""
    for s in range(16):
        salt += random.choice(ALPHABET)
    return salt


def generate_token(name):
    return hashlib.md5(name.encode('utf-8')).hexdigest() + generate_salt()


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=0)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


def insert_name(name, token):
    collection.insert_one({'token': token, 'name': name, 'is_open': False})


@app.route('/trace')
def trace_mail():
    token = request.args.get('token')
    find = collection.find_one({'token': token})
    print('token is {0}'.format(token))
    if not find:
        return Response(status=400)
    collection.find_one_and_update(
        {'token': token}, {'$set': {'is_open': True}})
    img = Image.new('RGB', size=(1, 1), color='white')
    return serve_pil_image(img)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
