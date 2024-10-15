from flask import Flask, render_template, redirect
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_required
from db import make_session
from models import User, VideoStreams
from sqlalchemy import select

load_dotenv()

LOGIN_APP = os.getenv("LOGIN_APP")
UPLOAD_APP = os.getenv("UPLOAD_APP")
FILESYSTEM_APP = os.getenv("FILESYSTEM_APP")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = LOGIN_APP + "/login"


@login_manager.user_loader
def load_user(user_id):
    session = make_session()
    user = session.get(User, user_id)
    session.close()
    return user


@app.route("/")
@login_required
def index():
    session = make_session()
    query = session.scalars(select(VideoStreams))
    results = [result.to_dict() for result in query]
    session.close()
    return render_template("index.html",
                           FILESYSTEM_APP=FILESYSTEM_APP,
                           results=results)


@app.route("/upload")
def upload():
    return redirect(UPLOAD_APP)


@app.route("/logout")
@login_required
def logout():
    return redirect(LOGIN_APP + "/logout")


if __name__ == "__main__":
    app.run(debug=True, port=8090, host="0.0.0.0")
