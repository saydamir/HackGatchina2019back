from pymongo import MongoClient, GEO2D
from bson.json_util import dumps
import datetime
import os
from flask import Flask, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
import hashlib
import json

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient('localhost', 27017)

db = client['gatchina']
collection = db['problems']
collection.create_index([("coordinate", GEO2D)])

@app.route('/issues', methods=['POST'])
def post_issue():
    content = request.get_json()
    # post = {"author": "Mike",
            # "text": "My first blog post!",
            # "coordinate": "33.44, 55.22",
            # "date": datetime.datetime.utcnow()}
    content["create_date"] = datetime.datetime.now().strftime("%d/%m/%Y")
    post_id = collection.insert_one(content).inserted_id
    return str(post_id)

@app.route('/issues', methods=['GET'])
def get_issues():
    documents = []
    for document in collection.find():
        documents.append(document)
    return dumps(documents)

@app.route('/issues/coordinate/<coordiante>', methods=['GET'])
def get_issues_near(coordiante):
    coordinate_list = coordiante.split(",")
    x, y = float(coordinate_list[0]), float(coordinate_list[1])
    documents = []
    for document in collection.find({"coordinate": {"$near": [x, y]}}).limit(20):
        documents.append(document)
    return dumps(documents)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/images', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename =  hashlib.md5(file.read()).hexdigest() + "." + secure_filename(file.filename).rsplit('.', 1)[1].lower()
            file.seek(0)
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

@app.route('/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join("", filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

@app.route('/', methods=['GET'])
def main_page_template():
    documents = []
    for document in collection.find():
        documents.append(document)
        documents.sort(key=lambda i: len(i['users_like']), reverse=True)
    print(documents)
    return render_template("issues.html",
        title = 'Home',
        documents = documents)

@app.route('/webissue/<id>', methods=['GET'])
def issue_page_template(id):
    issue = collection.find_one({"_id" : id})
    return render_template("issue.html",
        title = 'Issue',
        issue = issue)


@app.route('/static/', defaults={'path': ''})
@app.route('/static/<path:path>')
def get_resource(path):  # pragma: no cover
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".js": "application/javascript",
    }
    complete_path = os.path.join("./static", path)
    ext = os.path.splitext(path)[1]
    mimetype = mimetypes.get(ext, "text/html")
    content = get_file(complete_path)
    return Response(content, mimetype=mimetype)