from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timezone
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

try:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")
    print("connected to MongoDB")
except Exception as e:
    print("MongoDB connection failed:", e)

db = client[DB_NAME]
users = db["users"]
experiences = db["experiences"]
bucketlist = db["bucketlist"]


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    all_exp = list(experiences.find({"user_id": session["user_id"]}).sort("rating", -1))
    for i, exp in enumerate(all_exp, start=1):
        exp["rank"] = i
    return render_template("home.html", experiences=all_exp)

# SIGN UP/LOGIN/AUTHENTICATION
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        users.insert_one({"name": name, "email": email, "password": password})
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users.find_one({"email": email, "password": password})
        if user:
            session["user_id"] = str(user["_id"])
            session["name"] = user["name"]
            return redirect(url_for("home"))
        else:
            return render_template("login_error.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# PROFILE 
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    exps = list(experiences.find({"user_id": session["user_id"]}).sort("created_at", -1))
    return render_template("profile.html", name=session["name"], experiences=exps)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = users.find_one({"_id": ObjectId(session["user_id"])})
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        users.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$set": {"name": name, "email": email}}
        )
        session["name"] = name
        return redirect(url_for("profile"))
    return render_template("edit_profile.html", user=user)

# EXPERIENCES
@app.route("/add", methods=["GET", "POST"])
def add_experience():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        notes = request.form["notes"]
        rating = float(request.form["rating"])
        picture = request.files.get("picture")
        filename = None
        if picture and picture.filename:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        new_exp = {
            "title": title,
            "category": category,
            "notes": notes,
            "rating": rating,
            "picture": filename,
            "user_id": session["user_id"],
            "created_at": datetime.now(timezone.utc)
        }
        experiences.insert_one(new_exp)
        return redirect(url_for("home"))
    return render_template("add_experience.html")

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_experience(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    exp = experiences.find_one({"_id": ObjectId(id)})
    if not exp:
        return "Experience not found", 404
    next_page = request.args.get('next', 'profile')
    if request.method == "POST":
        updated = {
            "title": request.form["title"],
            "category": request.form["category"],
            "notes": request.form["notes"],
            "rating": float(request.form["rating"])
        }
        picture = request.files.get("picture")
        if picture and picture.filename:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            updated["picture"] = filename
        else:
            updated["picture"] = exp.get("picture")
        experiences.update_one({"_id": ObjectId(id)}, {"$set": updated})
        return redirect(url_for(next_page))
    return render_template("edit_experience.html", exp=exp)

@app.route("/delete/<id>")
def delete_experience(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    next_page = request.args.get('next', 'profile')
    experiences.delete_one({"_id": ObjectId(id)})
    return redirect(url_for(next_page))

# BUCKETLIST
@app.route("/your_lists")
def your_lists():
    if "user_id" not in session:
        return redirect(url_for("login"))
    all_items = list(bucketlist.find({"user_id": session["user_id"]}).sort("rating", -1))
    for i, item in enumerate(all_items, start=1):
        item["rank"] = i
    return render_template("your_lists.html", bucketList=all_items)

@app.route("/add_bucketlist", methods=["GET", "POST"])
def add_bucketlist():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        notes = request.form["notes"]
        rating = float(request.form["rating"])
        picture = request.files.get("picture")
        filename = None
        if picture and picture.filename:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        new_item = {
            "title": title,
            "category": category,
            "notes": notes,
            "rating": rating,
            "picture": filename,
            "user_id": session["user_id"]
        }
        bucketlist.insert_one(new_item)
        return redirect(url_for("your_lists"))
    return render_template("add_bucketlist.html")

@app.route("/bucketlist/edit/<id>", methods=["GET", "POST"])
def edit_bucketlist(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    item = bucketlist.find_one({"_id": ObjectId(id)})
    if not item:
        return "Item not found", 404
    if request.method == "POST":
        updated = {
            "title": request.form["title"],
            "category": request.form["category"],
            "notes": request.form["notes"],
            "rating": float(request.form["rating"])
        }
        picture = request.files.get("picture")
        if picture and picture.filename:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            updated["picture"] = filename
        else:
            updated["picture"] = item.get("picture")
        bucketlist.update_one({"_id": ObjectId(id)}, {"$set": updated})
        return redirect(url_for("your_lists"))
    return render_template("edit_bucketlist.html", exp=item)

@app.route("/bucketlist/delete/<id>")
def delete_bucketlist(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    bucketlist.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("your_lists"))

@app.route("/bucketlist/complete/<id>", methods=["POST"])
def complete_bucketlist(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    item = bucketlist.find_one({"_id": ObjectId(id)})
    if not item:
        return "Item not found", 404
    new_exp = {
        "title": item["title"],
        "category": item.get("category", ""),
        "notes": item.get("notes", ""),
        "rating": float(item.get("rating", 0)),
        "picture": item.get("picture"),
        "user_id": session["user_id"],
        "created_at": datetime.now(timezone.utc)
    }
    experiences.insert_one(new_exp)
    bucketlist.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("your_lists"))

# SEARCH 
@app.route('/search')
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template('search.html')


if __name__ == "__main__":
    app.run(debug=True)
