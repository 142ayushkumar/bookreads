import os

from flask import Flask, session, render_template, redirect, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_paginate import Pagination, get_page_args


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if 'username' in session:
        return render_template("index.html", username=session["username"])
    else:
        return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect("/")
    else:
        print(request.method)
        if "log-in" in request.form:
            username = request.form['username']
            password = request.form['password']
            login = 'Username or Password is incorrect'
            print("error source")
            if db.execute("SELECT * FROM users WHERE username= :username AND password= :password", {"username": username, "password": password}).rowcount == 0:
                return render_template("login.html", login=login, error=True)
            else:
                session['username'] = username
                return redirect("/")
        elif "sign-up" in request.form:
            print("here11")   
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            if len(password) == 0 or len(username) == 0 or len(email) == 0:
                signup = 'any of the field can\'t be blank'
                return render_template("login.html", signup=signup, error1=True)
            try:
                db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)", {"email":email, "username":username, "password":password})
                db.commit() 
                session['username'] = username
                return redirect("/")
            except:
                signup = 'username or email exists, please try different username and/or email'
                return render_template("login.html", signup=signup, error1=True)
        else:
            return render_template("login.html")


@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

books = db.execute("SELECT * FROM books").fetchall()
def get_books(offset=0, per_page=10):
    return books[offset: offset + per_page]

@app.route('/books/')
def show_books():
    #books = db.execute("SELECT * FROM books").fetchall()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(books)
    pagination_books = get_books(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('books.html',
                           books=pagination_books,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )
    