from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
app = Flask(__name__)

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
        experience = {
            "title": request.form['title'],
            "category": request.form['category'],
            "notes": request.form['notes'],
            "rating": float(request.form['rating'])
        }
        experiences_collection.insert_one(experience)
        return redirect(url_for('home'))
    return render_template('add_experience.html')

@app.route('/delete/<id>')
def delete_experience(id):
    from bson.objectid import ObjectId
    experiences_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
