from flask import Flask, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Integer, Float, Table, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, TimeField, SelectField, BooleanField, IntegerField, FloatField
from wtforms.validators import DataRequired
import sqlite3
from wtforms.validators import DataRequired, Length
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
bs = Bootstrap5(app=app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db.init_app(app=app)
app.config['SECRET_KEY'] = 'secretkey'


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()],
                           render_kw={
                               "class": "Username",
                               "placeholder": "Enter Your Username"
                           })
    password = StringField("Password", validators=[DataRequired()],
                           render_kw={
                               "class": "password",
                               "placeholder": "Enter Your Password"
                           })
    submit = SubmitField("Login", render_kw={"class": "button"})


class RegisterForm(FlaskForm):
    name = StringField("username", validators=[DataRequired(), Length(min=6, max=10)],
                           render_kw={
                               "class": "Username",
                               "placeholder": "Enter Your Username"
                           })
    username = StringField("username", validators=[DataRequired(), Length(min=6, max=10)],
                           render_kw={
                               "class": "Username",
                               "placeholder": "Enter Your Username"
                           })
    password = StringField("password", validators=[DataRequired(), Length(min=8, max=14)],
                           render_kw={
                               "class": "password",
                               "placeholder": "Enter Your Username"
                           })
    submit = SubmitField("Register",render_kw={"class": "button"})

class ToDoForm(FlaskForm):
    to_do = StringField("ToDo Task", validators=[DataRequired()],
                           render_kw={
                               "class": "todobox",
                               "placeholder": "Enter The Task"
                           })
    submit = SubmitField("Add", render_kw={"class": "button"})

class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    username: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)


class ToDo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    todo: Mapped[str] = mapped_column(String, nullable=False)


@app.route("/", methods=["GET", "POST"])
def home_page():
    login_form = LoginForm()
    if request.method == "POST":
        user_name = login_form.username.data
        password = login_form.password.data
        print(user_name, password)
    return render_template("index.html", form=login_form)


@app.route("/register", methods=["GET","POST"])
def register_page():
    register_form = RegisterForm()
    if request.method == "POST":
        name = register_form.name.data
        username = register_form.username.data
        password = register_form.password.data
    return render_template("register.html",form=register_form)

@app.route("/todo", methods=["GET","POST"])
def todo_page():
    todo_form = ToDoForm()
    new_todo = todo_form.to_do.data

    return render_template("todo.html",form=todo_form)



if __name__ == "__main__":
    app.run()
