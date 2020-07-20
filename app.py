import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from os import path
if path.exists("env.py"):
    """ get env.py file for keys/URIs"""
    import env
    print("env.py imported")

""" congig new app """ 

# config flask
app = Flask(__name__)

# config mongo
app.config['MONGO_URI'] = os.getenv('MONGO_URI') 
app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
mongo = PyMongo(app)
app.secret_key = os.getenv("SECRET_KEY")

# create mongo collection variables
coll_users = mongo.db.users
coll_goals = mongo.db.goals
coll_app_stats = mongo.db.app_stats

""" index """ 
@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


""" login """

@app.route('/login')
def login():
    if 'username' in session:
        username=session['username']
        flash("You are logged in already!")
        return redirect(url_for('dashboard', username=username))
    else:
        return render_template("login.html")


@app.route('/login_auth', methods=['POST'])
def login_auth():
    """check username and password match a registered user"""
    registered_user = coll_users.find_one({'username': request.form.get('username')})
    if registered_user:
        if check_password_hash(registered_user['password'], request.form.get('password')):
            # redirect user to dash on successful login
            session['username'] = request.form.get('username')
            return redirect(url_for("dashboard", username=session['username']))
        else:
            # redirect user to login if incorrect password
            flash("That looks like the wrong password. Please try again.")
            return redirect(url_for("login"))
    else:
        # redirect user to signup if username not found in mongo
        flash("It doesn't look like you've registered with us yet. Sign up today!")
        return redirect(url_for("signup"))

""" signup """ 
@app.route('/signup')
def signup():
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)