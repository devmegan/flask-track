import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
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
    # redirect user to dash if already logged in
    if 'username' in session:
        username = session['username']
        flash("You are logged in already! If you want to register a new account, please log out first.")
        return redirect(url_for('dashboard', username=username))
    else:
        return render_template("signup.html")


@app.route('/register_user', methods=['POST'])
def register_user():
    existing_email = coll_users.find_one({"email": request.form.get('email')})
    existing_user = coll_users.find_one({"username": request.form.get('username')})
    # server-side registration validation
    if request.form.get('password') == request.form.get('passwordcheck'):
        if not existing_email:
            if not existing_user:
                pw_hashed = generate_password_hash(request.form.get('password'))
                # if it's all good, insert new user into mongo users collection
                coll_users.insert_one({
                    'fname': request.form.get('fname'),
                    'lname': request.form.get('lname'),
                    'username': request.form.get('username'),
                    'email': request.form.get('email'),
                    'password': pw_hashed,
                    'signup_date': datetime.today(),
                    'goals_number': 0,
                    'goals_achieved': 0,
                    'deposits_number': 0,
                    'withdrawals_number': 0,
                    'currency': request.form.get('currency'),
                    'total_saved': 0,
                    'total_achieved': 0
                }) 
                flash("Please login with your new details")
                return redirect(url_for("login"))
            else:
                flash("Sorry, that username is already taken")
                return redirect(url_for("signup"))
        else:
            flash("Sorry, it looks like that email address is already registered with us")
            return redirect(url_for("signup"))
    else:
        flash("Sorry, it looks like your passwords didn't match")
        return redirect(url_for("signup"))


""" dashboard """ 
@app.route('/dashboard/<username>')
def dashboard(username):
    # send user to dashboard if username in session and it's theirs
    if 'username' in session and session['username'] == username:
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        user_savings_history = []
        for goal in list_goals:
            if goal['savings_history']: # don't execute if no savings activity yet
                for item in goal['savings_history']:
                    item.append(goal['goal_name'])
                    user_savings_history.append(item)
        user_savings_history.sort(key=lambda x: x[0])  # sort total savings by date
        return render_template("dashboard.html", user=current_user, goals=list_goals, user_savings_history=user_savings_history)
    else:
        flash("Please login to view your dashboard")
        return redirect(url_for("login"))

""" user profile """ 
@app.route('/profile/<username>')
def profile(username):
    if 'username' in session and session['username']==username:  # check to make sure not accessing another usernames account
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        return render_template("profile.html", user=current_user, goals=list_goals)
    else:
        flash("Please login to view your profile")
        return redirect(url_for("login"))


""" logout """
@app.route('/logout')
def logout():
    session.clear()
    flash("You have logged out of your account")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)