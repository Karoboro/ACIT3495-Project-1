from flask import Flask, render_template, redirect, url_for, flash
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from db import make_session
from models import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

load_dotenv()

UPLOAD_APP = os.getenv("UPLOAD_APP")
STREAM_APP = os.getenv("STREAM_APP")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    # Not able to figure out a way to keep checking for login using login_service
    session = make_session()
    user = session.get(User, user_id)
    session.close()
    return user


def CheckUsername():
    def username_check(form, field):
        if not field.data.isalnum():
            raise ValidationError("Username contains special characters!")
        session = make_session()
        user_exist = session.execute(
            select(User).where(User.username == field.data)
        ).scalar_one_or_none()
        if user_exist:
            raise ValidationError(f"Username {field.data} already exists!")

    return username_check


class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=32)],
        render_kw={"placeholder": "Username", "autofocus": True},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=32)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=32), CheckUsername()],
        render_kw={"placeholder": "Username", "autofocus": True},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=32)],
        render_kw={"placeholder": "Password"},
    )
    re_password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=32)],
        render_kw={"placeholder": "Re-enter Password"},
    )
    submit = SubmitField("Register")


@app.route("/upload")
def index():
    return redirect(UPLOAD_APP)


@app.route("/stream")
def stream():
    return redirect(STREAM_APP)


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(UPLOAD_APP)
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        session = make_session()
        user = session.scalar(select(User).where(User.username == form.username.data))
        if not user or not user.check_password(form.password.data):
            flash("Wrong username or password")
            return render_template("login.html", form=form)
        login_user(user)
        return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(UPLOAD_APP)
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.re_password.data:
            flash("Passwords do not match!")
            return render_template("register.html", form=form)
        session = make_session()
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        session.close()
        flash(f"Account {form.username.data} registered!")
        return redirect(url_for("login"))
    else:
        if form.username.errors:
            flash(form.username.errors[-1])
    return render_template("register.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


def inject_sample():
    session = make_session()
    user = User(username="SampleUser")
    user.set_password("samplepassword")
    try:
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    inject_sample()
    app.run(debug=True, port=8000, host="0.0.0.0")
