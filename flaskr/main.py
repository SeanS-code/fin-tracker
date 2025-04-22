from flask import Flask, render_template, request, url_for, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["tracker"]
collection = db["expenses"]

# Base page
@app.route('/', methods=('GET', 'POST'))
def root():
    if request.method=='POST':
        content = request.form['groceries']
        price = int(content)
        collection.insert_one({'groceries': price})
        return redirect(url_for('root'))
    
    return render_template('index.html')

"""

GET
>> for login authentication and authorization

>> for a users expenses in database
(users and expenses are connected through an id)

>> for displaying the expenses on the page
(select that matches the time chosen by user)

CREATE
>> create an expense with...
1) category (groceries, leisure, electronics ...)
2) value ($75, $100)
3) date (3.15.2020, 4.15.2025)

>> create a user with...
username
password

UPDATE
>> update expenses (change category, value or date)

DELETE
>> delete existing expenses

"""