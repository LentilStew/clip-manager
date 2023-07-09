from flask import Flask, request
from youtube_upload.youtube import pipe_bucket_to_youtube
from google.oauth2.credentials import Credentials
import json
import logging
from flask import jsonify
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    bucket_name = request.json["bucket_name"]
    bucket_file = request.json["bucket_file"]
    request_body = json.loads(request.json["request-body"])
    credentials_json = json.loads(request.json["credential"])
    logging.info("Checking credentials")
    for i in range(500):
        print("TEST PRINT")
        logging.info("TEST LOGGING")
    try:
        credential:Credentials = Credentials.from_authorized_user_info(credentials_json) 
    except Exception as e:
        logging.error(e)
        return jsonify(message="Invalid credentials!"), 400
    
    logging.info("Credentials are valid")

    try:
        pipe_bucket_to_youtube(bucket_name, bucket_file,credential,request_body)
    except Exception as e:
        logging.error(e)
        return jsonify(message="Upload failed!"), 400
    
    logging.info("File uploaded successfully!")

    return jsonify(message="File uploaded successfully!"), 200

if __name__ == "__main__":
    app.run(port=8080,host='0.0.0.0')