#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL

from sqlhelpers import *
from forms import *
from functools import wraps

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'blueCoin'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
#had to initialize the app before calling sqlhelpers (partially initialized...)
def log_in_user(username):
    users = Table("users", "name", "email", "username", "password")
    user = users.getone("username", username)

    session['logged_in'] = True
    session['username'] = username
    session['name'] = user.get("name")
    session['email'] = user.get("email") #add user.get('balance') ? 

    return True

def is_logged_in(func): #function to use for pages that should only be accessible if a user is logged in 
    @wraps(func)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return func(args, **kwargs)
        else:
            flash("unauthorized, please login", "danger")
            return redirect(url_for('login'))
    return wrap

@app.route('/login', methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        passAttempt = request.form['password']

        users = Table('users', 'name', 'email', 'username', 'password')
        user = users.getone("username", username)

        accPassword = user.get('password')

        if accPassword is None:
            flash("Username is not found", "danger") 
            return redirect(url_for('login'))
        elif sha256_crypt.verify(passAttempt, accPassword):
            log_in_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("invalid password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('successfully logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    users = Table('users', 'name', 'email', 'username', 'password')
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        name = form.name.data
        if isnewuser(username) == True:
            passwordHash = sha256_crypt.encrypt(form.password.data) #might need to update this deprecated method
            users.insert(name,email,username,passwordHash)
            log_in_user(username)
            return redirect(url_for('dashboard'))
        else:
            print('flash message')
            flash('User already exists', 'danger') #flash message defined inside includes file
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug = True)
