import hashlib
import random
from pymongo import MongoClient
from flask import Flask, request, Response

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


def get_name():
    return ''


@app.route('/trace')
def trace_mail():
    token = request.args.get('token')
    find = collection.find_one({'token': token})
    if not find:
        return Response(status=400)
    collection.find_one_and_update(
        {'token': token}, {'$set': {'is_open': True}})
    return Response(status=200)


@app.route('/token')
def token():
    name = get_name()
    token = generate_token(name)
    collection.insert_one({'token': token, 'name': name, 'is_open': False})
    return Response(status=200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
