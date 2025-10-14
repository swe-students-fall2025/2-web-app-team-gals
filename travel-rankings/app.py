from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

load_dotenv()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

try:
    client = MongoClient(MONGO_URI)
    client.admin.command("ping")
    print("Connected to MongoDB")

except Exception as e:
    print("MongoDB connection failed", e)

db = client[DB_NAME]
experiences = db["experiences"]

@app.route("/")
def home():
    all_exp = list(experiences.find().sort("rating", -1))

    for i, exp in enumerate(all_exp, start=1):
        exp["rank"] = i

    return render_template("home.html", experiences=all_exp)

@app.route("/add", methods=["GET", "POST"])
def add_experience():
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
            "picture": filename
        }
        experiences.insert_one(new_exp)
        return redirect(url_for("home"))

    return render_template("add_experience.html")


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit_experience(id):
    exp = experiences.find_one({"_id": ObjectId(id)})
    if not exp:
        return "Experience not found", 404

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
        return redirect(url_for("home"))

    return render_template("edit_experience.html", exp=exp)


@app.route("/delete/<id>")
def delete_experience(id):
    experiences.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
