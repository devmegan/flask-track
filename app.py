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

""" config new app """ 

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
    app_stats = coll_app_stats.find_one({"rec_name": "user_stats"})
    if 'username' in session: 
        username=session['username']
        current_user = coll_users.find_one({"username": username})
        return render_template("index.html", user=current_user, app_stats=app_stats)
    else:
        return render_template("index.html", app_stats=app_stats)


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
    # prep currency switch val
    if request.form.get('currency') == "on":
        currency = "€"
    else:
        currency = "£"
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
                    'goals_achieved': [],
                    'deposits_number': 0,
                    'withdrawals_number': 0,
                    'currency': currency,
                    'total_currently_saved': 0,
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


""" user goals """ 


@app.route('/view_goal/<username>/<goal_id>')
def goal_view(username, goal_id):
    # check to make sure not accessing another usernames account
    if 'username' in session and session['username']==username:
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        current_goal = coll_goals.find_one({"_id": ObjectId(goal_id)}) # convert goal id into bson, then find id in mongo db that matches it
        return render_template("viewgoal.html", user=current_user, goal=current_goal, goals=list_goals)
    else:
        flash("Please login to view your goals")
        return redirect(url_for("login"))


""" savings history """


@app.route('/savingshistory/<username>', defaults={'goal_id': ''})
@app.route("/savingshistory/<username>/<goal_id>")
def savingshistory(username, goal_id):
    if 'username' in session and session['username'] == username:
        current_user = coll_users.find_one({"username": username})
        if not goal_id:
            flash("fullhistory")
            list_goals = list(coll_goals.find({"username": username}))
            user_savings_history = []
            for goal in list_goals:
                if goal['savings_history']: # don't execute if no savings activity yet
                    for item in goal['savings_history']:
                        item.append(goal['goal_name'])
                        user_savings_history.append(item)
                        user_savings_history.sort(key=lambda x: x[0])  # sort total savings by date
            return render_template("savingshistory.html", user=current_user, user_savings_history=user_savings_history, historytype="user")
        elif goal_id:
            flash("goal history")
            current_goal = coll_goals.find_one({"_id": ObjectId(goal_id)})
            return render_template("savingshistory.html", user=current_user, historytype="goal", goal=current_goal)
    else:
        flash("Please login to view your savings history")
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


@app.route('/update_user/<username>', methods=['POST'])
def update_user(username):
    existing_email = coll_users.find_one({"email": request.form.get('email')})
    existing_user = coll_users.find_one({'username': username})
    # prep currency if user has switched it
    if request.form.get('currency-switch') == "on":
        if existing_user['currency'] == "£":
            currency = "€"
        else:
            currency = "£"
    else:
        currency = existing_user['currency']
    # check old pw successfuly confirmed
    if check_password_hash(existing_user['password'], request.form.get('password')): 
        # check email address will still be unique to user
        if not existing_email or request.form.get('email') == existing_user['email']:
            coll_users.update_one({"username": existing_user['username']},{'$set': {"fname": request.form.get('fname'), "lname": request.form.get('lname'), "email": request.form.get('email'), "currency": currency}})
            flash("Your profile has been updated")
            return redirect(url_for('profile', username=username))
        else: 
            flash("Sorry, it looks like that email address is already registered") 
            return redirect(url_for('profile', username=username))
    else: 
        flash("It looks like you entered your existing password incorrectly")
        return redirect(url_for('profile', username=username))


@app.route('/update_password/<username>', methods=['POST'])
def update_password(username):
    existing_user = coll_users.find_one({'username': username})
    # if old pw correct and new passwords match, insert new pw hash into mongo
    if check_password_hash(existing_user['password'], request.form.get('oldpassword')):  
        if request.form.get('newpassword') == request.form.get('newpasswordcheck'): 
            pw_hashed = generate_password_hash(request.form.get('newpassword')) 
            coll_users.update_one({"username": existing_user['username']},{'$set': {"password": pw_hashed}})
            flash("Your password has been updated")
            return redirect(url_for('profile', username=username))
        else: 
            flash("Sorry, it looks like your new passwords didn't match")
            return redirect(url_for('profile', username=username))
    else:
        flash("Sorry, it looks like you entered your old password incorrectly")
        return redirect(url_for('profile', username=username))


@app.route('/delete_user/<username>', methods=['POST'])
def delete_user(username):
    user_to_delete = coll_users.find_one({'username': username})
    # prevent users deleting test account
    if username != "testacc" and username != "ascipio" and username != "ladama":
        # only delete if user has confirmed password
        if check_password_hash(user_to_delete['password'], request.form.get('password_delete')):
            coll_users.remove({'username': username})
            coll_goals.remove({'username': username})
            session.clear()
            flash("Your profile has been deleted from this app")
            return redirect(url_for('index'))
        else:
            # redirect user to profile if incorrect password
            flash("That looks like the wrong password. Please try again.")
            return redirect(url_for('profile', username=username))
    else:
        flash(username + " is a test account. You can't delete it.")
        return redirect(url_for('profile', username=username))


""" logout """
@app.route('/logout')
def logout():
    session.clear()
    flash("You have logged out of your account")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)