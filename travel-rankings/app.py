import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

try:
    client = MongoClient(mongo_uri)
    client.admin.command('ping')
    print("MongoDB connection successful")
except Exception as e:
    print("connection error", e)

db = client[db_name]
experiences_collection = db["experiences"]

@app.route('/')
def home():
    experiences = list(experiences_collection.find())
    return render_template('home.html', experiences=experiences)

@app.route('/add', methods=['GET', 'POST'])
def add_experience():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        notes = request.form['notes']
        rating = float(request.form['rating'])

        # Handle uploaded file
        picture = request.files.get('picture')
        picture_filename = None
        if picture:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            picture_filename = filename

        # Save to MongoDB
        experience = {
            "title": title,
            "category": category,
            "notes": notes,
            "rating": rating,
            "picture": picture_filename
        }
        experiences_collection.insert_one(experience)
        return redirect(url_for('home'))

    return render_template('add_experience.html')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_experience(id):
    exp = experiences_collection.find_one({"_id": ObjectId(id)})

    if not exp:
        return "Experience not found", 404

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        notes = request.form['notes']
        rating = float(request.form['rating'])

        # Optional: update photo if a new one is uploaded
        picture = request.files.get('picture')
        if picture and picture.filename:
            filename = secure_filename(picture.filename)
            picture.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            exp['picture'] = filename  # overwrite old one

        # Update MongoDB document
        experiences_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "title": title,
                "category": category,
                "notes": notes,
                "rating": rating,
                "picture": exp.get('picture')
            }}
        )

        return redirect(url_for('home'))

    return render_template('edit_experience.html', exp=exp)

@app.route('/delete/<id>')
def delete_experience(id):
    experiences_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
