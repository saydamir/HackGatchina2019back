from flask import Flask
from flask import request
from pymongo import MongoClient
import datetime


app = Flask(__name__)
client = MongoClient('localhost', 27017)

db = client['gatchina']
collection = db['problems']

@app.route('/new_problem', methods=['POST'])
def hello_world():
    content = request.get_json()
    print(type(content))
    post = {"author": "Mike",
            "text": "My first blog post!",
            "coordinate": "33.44, 55.22",
            "date": datetime.datetime.utcnow()}
    
    post_id = collection.insert_one(content).inserted_id
    return str(post_id)