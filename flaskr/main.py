from flask import Flask, render_template, request, url_for, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime, timezone, timedelta

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

# Add an expense
@app.route('/add', methods=['POST'])
def add_expense():
    category = request.form['categories']
    value = int(request.form['price'])
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    
    document = {
        'category': category,
        'value' : value,
        'date' : date
    }

    collections.insert_one(document)
    return redirect(url_for('root'))

# Delete an expense
@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    collections.delete_one({ '_id' : ObjectId(id)})
    return redirect(url_for('root'))

# Route user to updating page
@app.route('/stage_update/<id>', methods=['POST'])
def stage_update(id):
    return render_template('update.html', _id=id)

# Update given expense
@app.route('/update/<id>', methods=['POST'])
def update(id):
    category = request.form['categories']
    value = int(request.form['price'])
    date = datetime.strptime(request.form['date'])
    
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

# Filter
@app.route('/filter', methods=['GET'])
def filter():
    filter_value = request.args.get('filter')
    print(filter_value)

    if filter_value == 'tmonth':
        # Filter by the past 3 months
        three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
        filtered_expenses = collections.find({"date": {"$gte": three_months_ago}})
    
    elif filter_value == 'week':
        # Filter by the past week
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        filtered_expenses = collections.find({"date": {"$gte": one_week_ago}})
    
    elif filter_value == 'month':
        # Filter by the past month
        one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        filtered_expenses = collections.find({"date": {"$gte": one_month_ago}})
    
    elif filter_value == 'custom':
        three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
        filtered_expenses = collections.find({"date": {"$gte": three_months_ago}})

    else:
        # If no valid filter is selected, display all expenses
        return redirect(url_for('root'))

    return render_template('index.html', collections=filtered_expenses)

@app.route('/login', methods=['GET'])
def login_direct():
    return render_template('auth/login.html')

@app.route('/register', methods=['GET'])
def register():
    return render_template('auth/register.html')