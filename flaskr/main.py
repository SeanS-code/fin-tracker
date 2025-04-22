from flask import Flask, render_template, request, url_for, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.tracker
collections = db.expenses

# Homepage
@app.route('/', methods=['GET'])
def root():
    all_expenses = collections.find()
    return render_template('index.html', collections=all_expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    category = request.form['categories']
    value = int(request.form['price'])
    date = request.form['date']
    
    document = {
        'category': category,
        'value' : value,
        'date' : date
    }

    collections.insert_one(document)
    return redirect(url_for('root'))

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    collections.delete_one({ '_id' : ObjectId(id)})
    return redirect(url_for('root'))

@app.route('/stage_update/<id>', methods=['POST'])
def stage_update(id):
    return render_template('update.html', _id=id)
@app.route('/update/<id>', methods=['POST'])
def update(id):
    category = request.form['categories']
    value = int(request.form['price'])
    date = request.form['date']
    
    collections.update_one(
        { '_id' : ObjectId(id)}, 
        { '$set': {
            'category': category,
            'value' : value,
            'date' : date    
        }}
    )
    print(id)
    return redirect(url_for('root'))