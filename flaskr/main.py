from flask import Flask, render_template, request, url_for, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.tracker
collections = db.expenses

# Base page
@app.route('/', methods=('GET', 'POST'))
def root():
    if request.method=='POST':
        print("Form submitted")
        category = request.form['categories']
        value = int(request.form['price'])
        date = request.form['date']
        
        collections.insert_one({'category': category, 'value': value, 'date': date})
        return redirect(url_for('root'))

    all_expenses = collections.find()
    return render_template('index.html', collections=all_expenses)
