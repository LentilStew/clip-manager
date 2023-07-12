from flask import Flask, request
from youtube_upload.youtube import pipe_bucket_to_youtube,delete_file_from_bucket
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
    delete_from_bucket = request.json.get("delete_from_bucket", False)

    logging.info("Checking credentials")
    try:
        credential:Credentials = Credentials.from_authorized_user_info(credentials_json) 
    except Exception as e:
        logging.error(e)
        return jsonify(message="Invalid credentials!"), 400
    
    logging.info("Credentials are valid")

    try:
        video_id = pipe_bucket_to_youtube(bucket_name, bucket_file,credential,request_body)
    except Exception as e:
        logging.error(e)
        return jsonify(message="Upload failed!"), 400
    
    if video_id is None:
        logging.error("Upload failed!")
        return jsonify(message="Upload failed!"), 400
        
    logging.info("File uploaded successfully!")

    if delete_from_bucket:
        logging.info("Deleting file from bucket")
        delete_file_from_bucket(bucket_name, bucket_file)
        
    return jsonify(message=video_id), 200

if __name__ == "__main__":
    app.run(port=8080,host='0.0.0.0')