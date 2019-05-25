from pymongo import MongoClient
import datetime
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import hashlib

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient('localhost', 27017)

db = client['gatchina']
collection = db['problems']

@app.route('/issues', methods=['POST'])
def post_issue():
    content = request.get_json()
    # post = {"author": "Mike",
            # "text": "My first blog post!",
            # "coordinate": "33.44, 55.22",
            # "date": datetime.datetime.utcnow()}
    
    post_id = collection.insert_one(content).inserted_id
    return str(post_id)

# @app.route('/issues', methods=['GET'])
# def get_issues():
    # cursor = collection.find({})
    # documents = []
    # for document in cursor:
        # documents.append(document)
    # 
    # print(documents)
    # return str(post_id)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/images', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = hashlib.md5(file.read()).hexdigest() + "." + secure_filename(file.filename).rsplit('.', 1)[1].lower()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return filename
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

from flask import send_from_directory

@app.route('/image/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)