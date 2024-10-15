from flask import Flask, request, send_from_directory, abort
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()

LOGIN_APP = os.getenv("LOGIN_APP")
UPLOAD_APP = os.getenv("UPLOAD_APP")
STREAM_APP = os.getenv("STREAM_APP")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/save', methods=["POST"])
def save():
    VIDEO_DIR = "videos/"
    os.makedirs(VIDEO_DIR, exist_ok=True)
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    file.save(os.path.join(VIDEO_DIR, filename))
    return "File saved", 200


@app.route('/videos/<filename>')
def videos(filename):
    VIDEO_DIR = "videos/"
    try:
        return send_from_directory(VIDEO_DIR, filename)
    except FileNotFoundError:
        abort(404)


if __name__ == "__main__":
    app.run(debug=True, port=8100, host="0.0.0.0")
