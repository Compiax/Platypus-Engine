import ocr
import os, timeit
from flask import Flask, request, redirect, url_for, jsonify, make_response, json
from werkzeug.utils import secure_filename
from werkzeug.wrappers import BaseResponse as Response

_uploadfolder = './bills'
_allowedextensions = set(['jpg','jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = _uploadfolder

@app.route('/', methods=['GET', 'POST'])
def upload_file():

    print("Finding File")
    file = request.files['file']

    print("Saving File")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    print("calling ocr")

    json_object = ocr.initiate_ocr("./bills/"+file.filename)

    resp = make_response(json_object,200)

    return resp

app.run(host='0.0.0.0')
