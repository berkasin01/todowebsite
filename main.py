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
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
bs = Bootstrap5(app=app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
db.init_app(app=app)
app.config['SECRET_KEY'] = 'secretkey'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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
    name = StringField("Name", validators=[DataRequired()],
                       render_kw={
                           "class": "Username",
                           "placeholder": "Enter Your Name"
                       })
    username = StringField("Username", validators=[DataRequired()],
                           render_kw={
                               "class": "Username",
                               "placeholder": "Enter Your Username"
                           })
    password = StringField("Password", validators=[DataRequired(), Length(min=8, max=14)],
                           render_kw={
                               "class": "password",
                               "placeholder": "Enter Your Password"
                           })
    submit = SubmitField("Register", render_kw={"class": "button"})


class ToDoForm(FlaskForm):
    to_do = StringField("ToDo Task", validators=[DataRequired()],
                        render_kw={
                            "class": "todobox",
                            "placeholder": "Enter The Task"
                        })
    submit = SubmitField("Add", render_kw={"class": "button"})


class User(db.Model, UserMixin):
    __tablename__ = "User"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    username: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    todos = relationship("ToDo", back_populates="parent")


class ToDo(db.Model):
    __tablename__ = "ToDo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id = mapped_column(ForeignKey("User.id"))
    todo: Mapped[str] = mapped_column(String, nullable=False)
    task_status: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    parent = relationship("User", back_populates="todos")


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def home_page():
    login_form = LoginForm()
    if request.method == "POST" and current_user.is_anonymous:
        user_name = login_form.username.data
        password = login_form.password.data
        user = db.session.execute(db.select(User).where(User.username == user_name)).scalar()
        if check_password_hash(user.password, password):
            login_user(user)
            print("True")
            return redirect(url_for('todo_page'))
    elif current_user.is_authenticated:
        return redirect(url_for("todo_page"))
    return render_template("index.html", form=login_form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    login_form = LoginForm()
    if request.method == "POST":
        user_name = login_form.username.data
        password = login_form.password.data
        user = db.session.execute(db.select(User).where(User.username == user_name)).scalar()
        if check_password_hash(user.password, password):
            login_user(user)
            print("True")
            return redirect(url_for('todo_page'))
    return render_template("login.html", form=login_form)


@app.route("/register", methods=["GET", "POST"])
def register_page():
    register_form = RegisterForm()
    if request.method == "POST":
        name = register_form.name.data
        username = register_form.username.data
        password = register_form.password.data
        pw_hash = generate_password_hash(password, method="scrypt", salt_length=8)
        new_user = User(
            name=name,
            username=username,
            password=pw_hash
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_page'))
    return render_template("register.html", form=register_form)


@app.route("/todo", methods=["GET", "POST"])
@login_required
def todo_page():
    todo_form = ToDoForm()
    task_status = 0
    todo_data = db.session.execute(db.select(ToDo).where(ToDo.parent_id == current_user.id)).scalars().all()
    if request.method == "POST":
        new_todo = todo_form.to_do.data
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%H:%M:%S")

        new_todo = ToDo(
            todo=new_todo,
            date=currentTime,
            task_status=task_status,
            parent_id=current_user.id
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('todo_page'))
    return render_template("todo.html", form=todo_form, all_data=todo_data)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("home_page"))


@app.route("/delete/<id_num>", methods=["GET", "POST"])
def delete(id_num):
    find_post = db.session.execute(db.select(ToDo).where(ToDo.id == id_num)).scalar()
    db.session.delete(find_post)
    db.session.commit()
    return redirect(url_for('home_page'))


@app.route("/complete/<id_num>", methods=["GET", "POST"])
def complete(id_num):
    find_post = db.session.execute(db.select(ToDo).where(ToDo.id == id_num)).scalar()
    find_post.task_status = 1
    db.session.commit()
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(debug=True)
