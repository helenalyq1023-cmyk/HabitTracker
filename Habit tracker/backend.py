import pymongo, flask
from pymongo import MongoClient
from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
import json
import os

mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client["Habit_tracker"]

#db.create_collection("score")

# Get the collections
users_collection = db["users"]
tasks_collection = db["tasks"]
user_tasks_collection = db["user_tasks"]
entertainment_collection = db["entertainment"]
completed_coll = db["completed_tasks"]
scr = db["score"]
user_entertainment_collection = db["user_entertainment"]

app = flask.Flask(__name__)
app.secret_key = "*784_liu%@sg"

@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        if 'user_name' in request.form:
            name = request.form['user_name']
            pw = request.form['pw']
            user = users_collection.find_one({'user_name': name})
            if user and check_password_hash(user['pw'], pw):
                session['user_name'] = name;
                usr = scr.find_one({"user_name": session['user_name']})
                if usr == None:
                    scr.insert_one({"user_name": session['user_name'], 
                        "emotion": 10,
                        "energy": 25,
                        "LRA": 0
                    })
                return redirect(url_for('home'))
            else:
                return render_template("login.html", err_msg = "Wrong password or username")
        else:
            return render_template("login.html")

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        if 'user_name' in request.form:
            name = request.form['user_name']
            pw = request.form['pw']
            if users_collection.find_one({'user_name': name}):
                return render_template("register.html", err_msg = "Username already exists")
            
            hashed_pw = generate_password_hash(pw)
            users_collection.insert_one({'user_name':name, 'pw':hashed_pw})
            
            return render_template("register.html")

@app.route('/home', methods = ["GET"])
def home():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    
    current_user = session['user_name']
    tasks = list(
        user_tasks_collection.find({"user_name": current_user})
        .sort("created_at", 1))
    entertainment = list(
        user_entertainment_collection.find({"user_name": current_user})
        .sort("created_at", 1)
    )
    scores = scr.find_one({"user_name": current_user})
    emo_val = scores["emotion"]
    energy_val = scores["energy"]
    LRA = scores["LRA"]
    err_msg_ent = session.pop('err_msg_ent', None)
    return render_template("home.html", 
                    tasks = tasks, 
                    emo_val = emo_val, 
                    energy_val = energy_val, 
                    lra = LRA, 
                    entertainment = entertainment, 
                    err_msg_ent = err_msg_ent)

@app.route('/add', methods = ["POST"])
def add():
    option = request.form.get("option")
    if option:
        user_tasks_collection.insert_one({
            "user_name": session['user_name'],
            "name": option,
            "created_at": datetime.now()
        })
    return redirect(url_for('home'))

@app.route('/entertain', methods = ["POST"])
def entertain():
    option = request.form.get("option")
    if option:
        user_entertainment_collection.insert_one({
            "user_name":session['user_name'],
            "name": option,
            "created_at": datetime.now()
        })
    return redirect(url_for('home'))

@app.route('/complete/<tsk_id>')
def complete(tsk_id):
    tsk = user_tasks_collection.find_one({"_id": ObjectId(tsk_id), "user_name": session["user_name"]})
    scores = scr.find_one({"user_name": session["user_name"]})
    tsk_scr = tasks_collection.find_one({"name": tsk["name"]})
    if tsk:
        completed_coll.insert_one({
            "user_name": session["user_name"],
            "name": tsk["name"],
            "created_at": tsk.get("created_at"),
            "completed_at": datetime.now()
        })
        emo_val = scores["emotion"]
        energy_val = scores["energy"]
        lra = scores["LRA"]
        emo_val += tsk_scr["emotion_cost"]
        energy_val += tsk_scr["energy_cost"]
        lra += tsk_scr["LRA_reward"]
        scr.delete_one({"user_name": session["user_name"]})
        scr.insert_one({
            "user_name": session["user_name"],
            "emotion": emo_val, 
            "energy":energy_val, 
            "LRA": lra
        })
        user_tasks_collection.delete_one({"_id": ObjectId(tsk_id), "user_name": session['user_name']})
    return redirect(url_for('home'))

@app.route('/delete/<tsk_id>')
def delete(tsk_id):
    user_tasks_collection.delete_one({"_id": ObjectId(tsk_id), "user_name": session["user_name"]})
    return redirect(url_for('home'))

@app.route('/complete_ent/<ent_id>')
def complete_ent(ent_id):
    ent = user_entertainment_collection.find_one({"_id": ObjectId(ent_id), "user_name": session["user_name"]})
    scores = scr.find_one({"user_name": session["user_name"]})
    ent_scr = entertainment_collection.find_one({"name": ent["name"]})
    if ent:
        emo_val = scores["emotion"]
        energy_val = scores["energy"]
        lra = scores["LRA"]
        emo_val += ent_scr["emotion_gain"]
        energy_val += ent_scr["energy_gain"]
        lra += ent_scr["LRA_cost"]
        print(ent_scr["LRA_cost"])
        if lra < 0:
            session['err_msg_ent'] = "Not enough LRA to complete this entertainment"
            return redirect(url_for('home'))
        completed_coll.insert_one({
            "user_name": session["user_name"],
            "name": ent["name"],
            "created_at": ent.get("created_at"),
            "completed_at": datetime.now()
        })
        scr.delete_one({"user_name": session["user_name"]})
        scr.insert_one({
            "user_name": session["user_name"],
            "emotion": emo_val, 
            "energy":energy_val, 
            "LRA": lra
        })
        user_entertainment_collection.delete_one({"_id": ObjectId(ent_id), "user_name": session['user_name']})
    return redirect(url_for('home'))

@app.route('/delete_ent/<ent_id>')
def delete_ent(ent_id):
    user_entertainment_collection.delete_one({"_id": ObjectId(ent_id), "user_name": session["user_name"]})
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host = "0.0.0.0", port = port)

