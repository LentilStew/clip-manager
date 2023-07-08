from flask import Flask, request
from youtube_upload.youtube import pipe_bucket_to_youtube
from google.oauth2.credentials import Credentials
import json
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    bucket_name = request.json["bucket_name"]
    bucket_file = request.json["bucket_file"]
    request_body = request.json["request-body"]

    credentials_json = json.loads( request.json["credential"])
    credential:Credentials = Credentials.from_authorized_user_info(credentials_json) 

    pipe_bucket_to_youtube(bucket_name, bucket_file,credential,request_body)
    return "File uploaded successfully!"

if __name__ == "__main__":
    app.run(port=8080)