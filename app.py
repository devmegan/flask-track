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
        """ load index page for user """
        username = session['username']
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        return render_template("index.html", user=current_user, app_stats=app_stats, goals=list_goals)
    else:
        """ load index page for nonuser """
        return render_template("index.html", app_stats=app_stats)


""" login """


@app.route('/login')
def login():
    if 'username' in session:
        """ redirect user to dash if in session """
        username = session['username']
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
    # fetch existing user data - check username/email will be unique
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
                    'total_achieved': 0,
                    'user_savings_history': []
                })
                app_total_users(1)
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
@app.route('/dashboard/<username>/', defaults={'add_goal': ''})
@app.route('/dashboard/<username>/<add_goal>')
def dashboard(username, add_goal):
    # send user to dashboard if username in session and it's theirs
    if 'username' in session and session['username'] == username:
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        user_savings_history = current_user['user_savings_history']
        # if add_goal decorator, first check if user has < 4 goals before routing to it
        if add_goal:
            # prevent user accessing add goal card if already 4 goals
            if current_user['goals_number'] == 4:
                flash("You can't add more than four goals")
                return render_template("dashboard.html", user=current_user, goals=list_goals, add_goal='', user_savings_history=user_savings_history)
            else:
                return render_template("dashboard.html", user=current_user, goals=list_goals, add_goal=add_goal, user_savings_history=user_savings_history)
        else:
            return render_template("dashboard.html", user=current_user, goals=list_goals, add_goal='', user_savings_history=user_savings_history)
    else:
        flash("Please login to view your dashboard")
        return redirect(url_for("login"))


""" user goals """


@app.route('/view_goal/<username>/<goal_id>')
def goal_view(username, goal_id):
    # check to make sure not accessing another usernames account
    if 'username' in session and session['username'] == username:
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        # convert goal id into bson, then find id in mongo db that matches it
        current_goal = coll_goals.find_one({"_id": ObjectId(goal_id)})
        all_deposits = []
        all_withdrawals = []
        for item in current_goal['savings_history']:
            if item[1] > 0:
                all_deposits.append(item[1])
            if item[1] < 0:
                all_withdrawals.append(abs(item[1]))
        # prep deposit/withdrawal stats
        date_today = date.today()
        if current_goal['deposits_number'] != 0:
            avg_deposit = sum(all_deposits)/len(all_deposits)
        else:
            avg_deposit = 0
        if current_goal['withdrawals_number'] != 0 and sum(all_withdrawals) != 0 and len(all_withdrawals) != 0:
            avg_withdrawal = sum(all_withdrawals)/len(all_withdrawals)
        else:
            avg_withdrawal = 0
        # prep savings forecast stats
        if current_goal['current_total'] != 0:
            if ((date_today - current_goal['start_date'].date()).days) != 0:
                avg_saved_perday = current_goal['current_total'] / ((date_today - current_goal['start_date'].date()).days)
                avg_needed_perday = current_goal['end_total'] / ((current_goal['end_date'].date() - date_today).days)
            else:
                avg_saved_perday = current_goal['current_total']
                avg_needed_perday = avg_needed_perday = current_goal['end_total']
            forecast_remaining_days = (current_goal['end_total'] - current_goal['current_total']) / avg_saved_perday
        else:
            avg_saved_perday = 0
            if ((current_goal['end_date'].date() - date_today).days) != 0:
                avg_needed_perday = (current_goal['end_total']) / ((current_goal['end_date'].date() - date_today).days)
            else:
                avg_needed_perday = (current_goal['end_total'])
            forecast_remaining_days = "unforcastable"  
        return render_template("viewgoal.html", user=current_user, goal=current_goal, goals=list_goals, avg_deposit=avg_deposit, avg_withdrawal=avg_withdrawal, all_deposits=all_deposits, all_withdrawals=all_withdrawals, date_today=date_today, avg_needed_perday=avg_needed_perday, avg_saved_perday=avg_saved_perday, forecast_remaining_days=forecast_remaining_days)
    else:
        flash("Please login to view your goals")
        return redirect(url_for("login"))


""" deposit or withdraw """


@app.route('/update_savings/<goal_id>/<action>', methods=['POST'])
def update_savings(goal_id, action):
    username = session['username']
    goal_to_update = coll_goals.find_one({"_id": ObjectId(goal_id)})
    old_end_total = goal_to_update['end_total']
    achieved_bool = goal_to_update['achieved']
    if action == 'withdraw':
        if abs(float((request.form.get('withdraw_value')))) > goal_to_update['current_total']:
            flash("You can't withdraw more than your current total")
            return redirect(url_for('goal_view', username=username, goal_id=goal_id))
        else: 
            update_value = 0 - abs(float((request.form.get('withdraw_value'))))
            deposits = goal_to_update['deposits_number']
            withdrawals = goal_to_update['withdrawals_number'] + 1
            action_complete = " withdrawn"
            # if goal was achieved, need to check if withdrawing will unachieve it
            if goal_to_update['achieved']:
                if(goal_to_update['current_total'] + update_value) < goal_to_update['end_total']:
                    achieved_bool = False
                    removing_value = 0 - goal_to_update['current_total']
                    app_goals_achieved(-1, removing_value)
    else:
        update_value = float(request.form.get('deposit_value'))
        deposits = goal_to_update['deposits_number'] + 1
        withdrawals = goal_to_update['withdrawals_number']
        action_complete = " deposited"
        # if goal not achieved, check to see if goal will now be reached with this deposit
        if not goal_to_update['achieved']:
            if (goal_to_update['current_total'] + update_value) >= goal_to_update['end_total']:
                achieved_bool = True
                adding_value = update_value + goal_to_update['current_total']
                app_goals_achieved(1, adding_value)
                user_goals_achieved = [goal_to_update['goal_name'], goal_to_update['current_total'] + update_value,  datetime.today()]
                coll_users.update_one({"username": username}, {'$push': {"goals_achieved": user_goals_achieved}})
     # set new total after withdraw/deposit
    updated_savings = goal_to_update['current_total'] + update_value
    # set maximum percent as 100, even if user saves over goal
    if int((updated_savings/old_end_total) * 100) > 100:
        percent_progress = 100
    else:
        percent_progress = int((updated_savings/old_end_total) * 100)
    # savings history for goal
    updated_savings_history = [datetime.today(), update_value]
    # savings history for user (incl. goal name)
    user_updated_savings_history = [goal_to_update['goal_name'], datetime.today(), update_value]
    # update goal 
    coll_goals.update_one({"_id": ObjectId(goal_id)}, {'$set': {"current_total": updated_savings, "percent_progress": percent_progress, "deposits_number": deposits, "withdrawals_number": withdrawals, "achieved": achieved_bool}})
    # push new activity go end of savings history arrays (goal and user)
    coll_goals.update_one({"_id": ObjectId(goal_id)}, {'$push': {"savings_history": updated_savings_history}})
    coll_users.update_one({"username": username}, {'$push': {"user_savings_history": user_updated_savings_history}})
    # update user's new deposits/withdrawals numbers
    coll_users.update_one({"username": username}, {'$set': {"deposits_number": deposits, "withdrawals_number": withdrawals}})
    # flash event to user - amount and whether deposited or withdrawn
    flash_currency = user_total_saved(username, update_value)
    flash(flash_currency + ('%.2f' % abs(update_value)) + action_complete)
    app_total_value(update_value)
    return redirect(url_for('goal_view', username=username, goal_id=goal_id))


""" edit goal """

@app.route('/update_goal/<goal_id>', methods=['POST'])
def update_goal(goal_id):
    username = session['username']
    current_user = coll_users.find_one({"username": username})
    goal_to_update = coll_goals.find_one({"_id": ObjectId(goal_id)})
    # prepare end_date var for insertion into mongodb 
    str_end_date = request.form.get('end_date')
    date_end_date = datetime.strptime(str_end_date, '%b %d, %Y')
    # prepare start and goal var for insertion into mongodb
    end_total = float(request.form.get('end_total').replace(",", ""))
    if end_total <= goal_to_update['current_total']:
        achieved_bool = True
        percent_progress = 100
        app_goals_achieved(1, goal_to_update['current_total'])
    else:
        achieved_bool = False
        app_goals_achieved(-1, goal_to_update['current_total'])
        percent_progress = int((goal_to_update['current_total']/end_total) * 100)
    coll_goals.update_one({'_id': ObjectId(goal_id)}, {'$set': {'goal_name':request.form.get('goal_name'), 'image_url':request.form.get('image_url'),'end_total': end_total,'percent_progress': percent_progress, 'end_date': date_end_date, 'achieved': achieved_bool}})
    return redirect(url_for('goal_view', username=username, goal_id=goal_id))



""" delete goal """


@app.route('/delete_goal/<goal_id>', methods=['POST'])
def delete_goal(goal_id):
    """ delete goal after password confirmed """
    username = session['username']
    user = coll_users.find_one({'username': username})
    # check submitted pw matched pw in mongo
    if check_password_hash(user['password'], request.form.get('password_delete')):
        coll_goals.remove({'_id': ObjectId(goal_id)})
        user_current_goals(-1)
        app_current_goals(-1)
        flash("Your goal has been deleted")
        return redirect(url_for('dashboard', username=username))
    else:
        # redirect user to profile if incorrect password
        flash("That looks like the wrong password. Please try again.")
        return redirect(url_for('goal_view', username=username, goal_id=goal_id))


""" insert new goal """


@app.route('/insert_goal', methods=['POST'])
def insert_goal():
    """ insert new goal into goals collection """
    username = session['username']
    search_keyword = str(request.form.get('search_keyword'))
    # prepare end_date var for insertion into mongodb 
    str_end_date = request.form.get('end_date')
    date_end_date = datetime.strptime(str_end_date, '%b %d, %Y')
    # prepare start and goal var for insertion into mongodb
    end_total = float(request.form.get('end_total').replace(',', ''))
    # insert new goal into mongodb
    coll_goals.insert_one({
        'username': username,
        'goal_name': request.form.get('goal_name'),
        'image_url': request.form.get('image_url'),
        'current_total': 0,
        'end_total': end_total,
        'percent_progress': 0,
        'start_date': datetime.today(),
        'deposits_number': 0,
        'withdrawals_number': 0,
        'savings_history': [],
        'end_date': date_end_date,
        'achieved': False
    })
    if search_keyword:
        """push anonymised list of keywords and returned images to db"""
        new_pair = [search_keyword, request.form.get('image_url')]  # array as mongodb doesn't take tuples
        coll_app_stats.update_one({"rec_name": "keyword_image_pairs"}, {'$push': {"pairs": new_pair}})
    user_current_goals(1)
    app_current_goals(1)
    return redirect(url_for('dashboard', username=username))


""" savings history """


@app.route('/savingshistory/<username>', defaults={'goal_id': ''})
@app.route("/savingshistory/<username>/<goal_id>")
def savingshistory(username, goal_id):
    """ display either user/goal history """
    if 'username' in session and session['username'] == username:
        current_user = coll_users.find_one({"username": username})
        # display entire user savings history
        if not goal_id:
            list_goals = list(coll_goals.find({"username": username}))
            user_savings_history = []
            for goal in list_goals:
                if goal['savings_history']:  # don't execute if no savings activity yet
                    for item in goal['savings_history']:
                        item.append(goal['goal_name'])
                        user_savings_history.append(item)
                        user_savings_history.sort(key=lambda x: x[0])  # sort savings history by date
            return render_template("savingshistory.html", user=current_user, user_savings_history=user_savings_history, historytype="user", goals=list_goals)
        # display history for a single goal
        elif goal_id:
            list_goals = list(coll_goals.find({"username": username}))
            current_goal = coll_goals.find_one({"_id": ObjectId(goal_id)})
            return render_template("savingshistory.html", user=current_user, historytype="goal", goal=current_goal, goals=list_goals)
    else:
        flash("Please login to view your savings history")
        return redirect(url_for("login"))


""" user profile """


@app.route('/profile/<username>')
def profile(username):
    """ load user profile populated with data from user collection """
    # check to make sure not accessing another usernames account
    if 'username' in session and session['username'] == username:
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        return render_template("profile.html", user=current_user, goals=list_goals)
    else:
        flash("Please login to view your profile")
        return redirect(url_for("login"))


@app.route('/update_user/<username>', methods=['POST'])
def update_user(username):
    """ update user profile with new currency/name/email """
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
    """ update user pw if existing pw confirmed """
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
    """ delete user once user pw confirmed """
    user_to_delete = coll_users.find_one({'username': username})
    # prevent users deleting test account
    if username != "testuser":
        # only delete if user has confirmed password
        if check_password_hash(user_to_delete['password'], request.form.get('password_delete')):
            coll_users.remove({'username': username})
            coll_goals.remove({'username': username})
            session.clear()
            app_total_users(-1)
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
    """ log user out and end session """
    session.clear()
    flash("You have logged out of your account")
    return redirect(url_for("index"))


""" 404 ERROR """


@app.errorhandler(404)
def page_not_found(e):
    """ 404 page if page not found """
    if 'username' in session:
        username = session['username']
        current_user = coll_users.find_one({"username": username})
        list_goals = list(coll_goals.find({"username": username}))
        return render_template("404.html", user=current_user, goals=list_goals), 404
    else: 
        return render_template("404.html"), 404


""" helper functions """


def user_current_goals(direction):
    """ increase/decrease number of total goals in app when goal is added/deleted """
    username = session['username']
    user = coll_users.find_one({"username": username})
    new_goals_number = user['goals_number'] + direction
    coll_users.update_one({"username": username}, {'$set': {"goals_number": new_goals_number}})
    return 

def app_current_goals(direction):
    """ increase/decrease number of total goals in app when goal is added/deleted """
    app_stats = coll_app_stats.find_one({"rec_name": "user_stats"})
    new_goals_current = app_stats['goals_current'] + direction
    coll_app_stats.update_one({"rec_name": "user_stats"}, {'$set': {"goals_current": new_goals_current}})
    return 

def user_total_saved(username, update_value):
    """ increase/decreases user total saved """
    user = coll_users.find_one({"username": username})
    new_saved_total = user['total_currently_saved'] + update_value
    coll_users.update_one({"username": username}, {'$set': {"total_currently_saved": new_saved_total}})
    user_currency = user['currency']
    return user_currency


def app_total_users(direction):
    """ increase/decrease total amount saved when user makes a signs up/deletes profile """
    app_stats = coll_app_stats.find_one({"rec_name": "user_stats"})
    new_user_total = app_stats['users_total'] + direction
    coll_app_stats.update_one({"rec_name": "user_stats"}, {'$set': {"users_total": new_user_total}})
    return


def app_total_value(amount):
    """ increase/decrease total amount saved when user makes a deposit/withdrawal """
    app_stats = coll_app_stats.find_one({"rec_name": "user_stats"})
    new_saved_total = app_stats['saved_total'] + amount
    coll_app_stats.update_one({"rec_name": "user_stats"}, {'$set': {"saved_total": new_saved_total}})
    return


def app_current_goals(direction):
    """ increase/decrease number of total goals in app when goal is added/deleted """
    app_stats = coll_app_stats.find_one({"rec_name": "user_stats"})
    new_goals_current = app_stats['goals_current'] + direction
    coll_app_stats.update_one({"rec_name": "user_stats"}, {'$set': {"goals_current": new_goals_current}})
    return


def app_goals_achieved(direction, value):
    """ increase/decreases goals achieved and achieved value """
    app_stats = coll_app_stats.find_one({"rec_name": "user_stats"})
    new_achieved_goals = app_stats['achieved_goals'] + direction
    new_achieved_value = app_stats['achieved_value'] + value
    coll_app_stats.update_one({"rec_name": "user_stats"}, {'$set': {"achieved_goals": new_achieved_goals, "achieved_value": new_achieved_value}})
    return

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=False