from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING, ASCENDING
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
friend_experiences = db["friend_experiences"]


@app.route("/api/feed")
def api_feed():
    all_exp = list(experiences.find({}, {"_id": 0}).sort("rating", -1))
    for i, exp in enumerate(all_exp, start=1):
        exp["rank"] = i
    return jsonify(all_exp)
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Friend's experiences
    friends_exps = list(
        friend_experiences.find({"user_id": {"$ne": session["user_id"]}})
        .sort("created_at", -1) 
    )
    # Add rank
    for i, exp in enumerate(friends_exps, start=1):
        exp["rank"] = i

    return render_template("home.html", experiences=friends_exps)

# POPULATE FRIENDS FEED
@app.route("/populate_friends_feed")
def populate_friends_feed():
    from datetime import datetime, timezone

    if friend_experiences.count_documents({}) > 0:
        return "Friend feed already populated!"
    
    friend_experiences.insert_many([
        {
            "title": "Skiing in Alps",
            "notes": "Snow was perfect!",
            "category": "Adventure",
            "rating": 10,
            "picture": "skiing.jpg",
            "friend_name": "Alice",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "Surfing in Hawaii",
            "category": "Beach",
            "notes": "Caught my first wave!",
            "rating": 9,
            "picture": None,
            "friend_name": "Bob",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "title": "Tokyo Food Tour",
            "category": "Food",
            "notes": "Sushi heaven",
            "rating": 10,
            "picture": None,
            "friend_name": "Charlie",
            "created_at": datetime.now(timezone.utc)
        }
    ])
    return "Friend feed populated!"

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

    # Next is now a FULL URL (e.g., "/profile"), not an endpoint name
    next_url = request.form.get("next") or request.args.get("next") or url_for("home")

    if request.method == "POST":
        # Cancel: do NOT save; just go back
        if "cancel" in request.form:
            return redirect(next_url)

        title = request.form.get("title", "")
        category = request.form.get("category", "")
        notes = request.form.get("notes", "")
        rating = float(request.form.get("rating", 0) or 0)
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
        return redirect(next_url)

    return render_template("add_experience.html", next=request.args.get("next", url_for("home")))

@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_experience(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    exp = experiences.find_one({"_id": ObjectId(id)})
    if not exp:
        return "Experience not found", 404

    next_page = request.args.get("next", request.form.get("next", "profile"))

    if request.method == "POST":
        if "cancel" in request.form:
            return redirect(url_for(next_page) if next_page in ["home", "profile", "feed", "your_lists"] else url_for("home"))

        updated = {
            "title": request.form.get("title", ""),
            "category": request.form.get("category", ""),
            "notes": request.form.get("notes", ""),
            "rating": float(request.form.get("rating", 0) or 0)
        }

        picture = request.files.get("picture")
        if picture and picture.filename:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            updated["picture"] = filename
        else:
            updated["picture"] = exp.get("picture")

        experiences.update_one({"_id": ObjectId(id)}, {"$set": updated})
        return redirect(url_for(next_page) if next_page in ["home", "profile", "feed", "your_lists"] else url_for("home"))

    return render_template("edit_experience.html", exp=exp, next=next_page)

@app.route("/delete/<id>")
def delete_experience(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    next_page = request.args.get('next', 'profile')
    experiences.delete_one({"_id": ObjectId(id)})
    return redirect(url_for(next_page))

# BUCKETLIST
@app.route("/your_bucketlist")
def your_bucketlist():
    if "user_id" not in session:
        return redirect(url_for("login"))
    all_items = list(bucketlist.find({"user_id": session["user_id"]}).sort("rating", -1))
    for i, item in enumerate(all_items, start=1):
        item["rank"] = i
    return render_template("your_bucketlist.html", bucketList=all_items)

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
        return redirect(url_for("your_bucketlist"))
    return render_template("add_bucketlist.html", exp={})

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
        return redirect(url_for("your_bucketlist"))
    return render_template("edit_bucketlist.html", exp=item)

@app.route("/bucketlist/delete/<id>")
def delete_bucketlist(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    bucketlist.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("your_bucketlist"))

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
    return redirect(url_for("your_bucketlist"))

@app.route("/feed_to_bucket/<id>", methods=["POST"])
def feed_to_bucket(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    friend_exp = friend_experiences.find_one({"_id": ObjectId(id)})
    if not friend_exp:
        return "Friend experience not found", 404

    new_bucket_item = {
        "title": friend_exp["title"],
        "category": friend_exp.get("category", ""),
        "notes": friend_exp.get("notes", ""),
        "rating": float(friend_exp.get("rating", 0)),
        "picture": friend_exp.get("picture"),
        "user_id": session["user_id"],
        "created_at": datetime.now(timezone.utc)
    }

    bucketlist.insert_one(new_bucket_item)

    return redirect(url_for("your_bucketlist"))

# SEARCH 
@app.route('/search', methods =["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        filtered_exp = get_filtered_experiences(request.form)  
        return render_template('search.html', experiences = filtered_exp)

    filtered_exp = get_filtered_experiences(request.args)
    return render_template('search.html', experiences = filtered_exp)

def get_filtered_experiences(form_data): 
    title = form_data.get("title", "").strip()
    category = form_data.get("category", "").strip()
    keywords = [k.strip() for k in form_data.get("keyword", "").split(" ") if k.strip()]
    rating_order = form_data.get("rating", "")

    query = {}

    if title: 
        query["title"] = {"$regex": title, "$options": "i"}

    if keywords: 
        keyword_clauses = []
        for kw in keywords: 
            regex = {"$regex": kw, "$options": "i"}
            keyword_clauses.extend([
                {"title": regex},
                {"category": regex},
                {"notes": regex} 
            ])
        query["$or"] = keyword_clauses

    if category: 
        query["category"] = {"$regex": category, "$options": "i"}

    sort_order = None
    if rating_order == "highLow":
        sort_order = [("rating", DESCENDING)]
    elif rating_order == 'lowHigh':
        sort_order = [("rating", ASCENDING)]

    if sort_order: 
        results = list(experiences.find(query).sort(sort_order))
    else: 
        results = list(experiences.find(query))       

    return results

@app.route('/your_lists')
def your_lists():
    all_exp = list(experiences.find().sort("rating", -1))

    for i, exp in enumerate(all_exp, start=1):
        exp["rank"] = i

    return render_template("your_lists.html", experiences=all_exp)


if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_SAMESITE=None,  
        SESSION_COOKIE_SECURE=False    
    )
    app.run(debug=True)
