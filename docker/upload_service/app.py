from flask import Flask, render_template, redirect, url_for, flash
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_required, current_user
from db import make_session
from models import User, VideoStreams
# import boto3
# from botocore.exceptions import ClientError
import uuid
import requests

load_dotenv()

LOGIN_APP = os.getenv("LOGIN_APP")
STREAM_APP = os.getenv("STREAM_APP")
FILESYSTEM_APP = os.getenv("FILESYSTEM_APP")
# AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
# AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
# S3_BUCKET = os.getenv("S3_BUCKET")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = LOGIN_APP + "/login"


def FileSizeLimit(max_size_in_mb):
    max_bytes = max_size_in_mb * 1024 * 1024

    def file_length_check(form, field):
        if len(field.data.read()) > max_bytes:
            raise ValidationError(f"File size must be less than {max_size_in_mb}MB")
        field.data.seek(0)
    return file_length_check


class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired(),
                                 FileAllowed(
                                     ['mp4'],
                                     "Invalid file format"),
                                 FileSizeLimit(100)])
    description = StringField(validators=[InputRequired(), Length(min=4)])
    submit = SubmitField("Upload")


# def upload_file(file_name, bucket):
#     object_name = os.path.basename(file_name)
#     s3_client = boto3.client(service_name='s3',
#                              region_name='us-west-2',
#                              aws_access_key_id=AWS_ACCESS_KEY,
#                              aws_secret_access_key=AWS_SECRET_KEY)
#     try:
#         response = s3_client.upload_file(file_name, bucket, object_name)
#     except ClientError:
#         return False
#     return object_name


@login_manager.user_loader
def load_user(user_id):
    session = make_session()
    user = session.get(User, user_id)
    session.close()
    return user


@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    form = UploadForm()
    if form.validate_on_submit():
        # UPLOAD_DIR = "upload_dir/"
        # os.makedirs(UPLOAD_DIR, exist_ok=True)
        _, file_extension = os.path.splitext(form.file.data.filename)
        # filename = UPLOAD_DIR + (secure_filename(form.file.data.filename)
        #                          or str(uuid.uuid4()) + file_extension)
        filename = (secure_filename(form.file.data.filename) or str(uuid.uuid4()) + file_extension)
        # form.file.data.save(filename)
        # object_name = upload_file(filename, S3_BUCKET)
        file = form.file.data
        files = {'file': (filename, file.stream, file.mimetype)}
        response = requests.post(f"{FILESYSTEM_APP}/save", files=files)
        if response.ok:
            session = make_session()
            video = VideoStreams(description=form.description.data,
                                 url=f"/videos/{filename}",
                                 user_id=current_user.id)
            session.add(video)
            session.commit()
            session.close()
            return redirect(url_for('index'))
        else:
            flash("File was not able to upload")
        # if object_name:
        #     flash("File successfully uploaded")
        #     os.remove(filename)
        #     url = f"https://{S3_BUCKET}.s3.us-west-2.amazonaws.com/{object_name}"
        #     video = VideoStreams(description=form.description.data,
        #                          url=url,
        #                          user_id=current_user.id)
        #     session = make_session()
        #     session.add(video)
        #     session.commit()
        #     session.close()
            # return redirect(url_for('index'))
        # else:
        #     flash("File was not able to upload")
    else:
        if form.file.errors:
            flash(form.file.errors[-1])
    return render_template("index.html", form=form)


@app.route('/stream')
def stream():
    return redirect(STREAM_APP)


@app.route('/logout')
@login_required
def logout():
    return redirect(LOGIN_APP + "/logout")


if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
