import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
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

# create mongo collection variables
coll_users = mongo.db.users
coll_goals = mongo.db.goals
coll_app_stats = mongo.db.app_stats

""" index """ 
@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'), port=int(os.environ.get('PORT')), debug=True)