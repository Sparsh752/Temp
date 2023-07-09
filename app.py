from flask import Flask, request,send_from_directory
from firebase_admin import credentials, initialize_app, storage
import subprocess
import os
from pydub import AudioSegment
import datetime
app = Flask(__name__,static_url_path='', static_folder='frontend/build')
from flask_cors import CORS
CORS(app)
cred = credentials.Certificate("./firebase_key.json")
initialize_app(cred, {'storageBucket': 'ethos-website-98c85.appspot.com'})
bucket = storage.bucket()
print('hello')
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/convert")
def convert():
    url = request.args.get('url')
    user = request.args.get('userid')
    filename=str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    output_path = filename+'.%(ext)s'
    command=['yt-dlp', '--extract-audio','--format','m4a', url, '-o', os.path.join(app.config['UPLOAD_FOLDER'],output_path)]
    print(os.path.join(app.config['UPLOAD_FOLDER'],output_path))
    process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    command=['ls']
    process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print(process)
    audio = AudioSegment.from_file(os.path.join(app.config['UPLOAD_FOLDER'],filename)+'.m4a', format='m4a')
    audio.export(os.path.join(app.config['UPLOAD_FOLDER'], filename)+'.mp3', format='mp3')
    blob = bucket.blob(user+'/'+filename+'.mp3')
    blob.upload_from_filename(os.path.join(app.config['UPLOAD_FOLDER'],filename)+'.mp3')
    blob.make_public()
    process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    command=['ls']
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename)+'.mp3')
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename)+'.m4a')
    process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    command=['ls']
    return user+'/'+filename+'.mp3'
@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')
if __name__ == '__main__':
    app.run()