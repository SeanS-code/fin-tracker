from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime, timezone, timedelta

import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.tracker
expense = db.expenses
user = db.users

# Page Routings

# Homepage
@app.route('/', methods=['GET'])
def root():
    if session.get('username') is None:
        return redirect(url_for('login'))
    userid = session.get('userid')
    username = session.get('username')

    all_expenses = expense.find({ 'user_id': ObjectId(userid)})
    return render_template('index.html', expense=all_expenses, username=username)

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        user_cred = user.find_one({'username': username, 'password': password})

        if  user_cred is not None:
            session['userid'] = str(user_cred['_id'])
            print('Session UserID:', session.get('userid'))
            session['username'] = username
            return redirect(url_for('root'))

    return render_template('auth/login.html')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        
        document = {
            'username': username,
            'password' : password
        }

        user.insert_one(document)
        return redirect(url_for('login'))
    return render_template('auth/register.html')

# Update Page
@app.route('/stage_update/<id>', methods=['POST'])
def stage_update(id):
    return render_template('update.html', _id=id)

# CRUDs for Expenses

# Add an expense
@app.route('/add', methods=['POST'])
def add_expense():
    category = request.form['categories']
    value = int(request.form['price'])
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    userid = session.get('userid')

    document = {
        'user_id': ObjectId(userid),
        'category': category,
        'value' : value,
        'date' : date
    }

    expense.insert_one(document)
    return redirect(url_for('root'))

# Delete an expense
@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    expense.delete_one({ '_id' : ObjectId(id)})
    return redirect(url_for('root'))

# Update given expense
@app.route('/update/<id>', methods=['POST'])
def update(id):
    category = request.form['categories']
    value = int(request.form['price'])
    date = datetime.strptime(request.form['date'])
    
    expense.update_one(
        { '_id' : ObjectId(id)}, 
        { '$set': {
            'category': category,
            'value' : value,
            'date' : date    
        }}
    )
    print(id)
    return redirect(url_for('root'))

# Filtering Expenses
@app.route('/filter', methods=['GET'])
def filter():
    filter_value = request.args.get('filter')
    userid = session.get('userid')

    if filter_value == 'tmonth':
        # Filter by the past 3 months
        three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
        filtered_expenses = expense.find({"user_id": ObjectId(userid), "date": {"$gte": three_months_ago}})
    
    elif filter_value == 'week':
        # Filter by the past week
        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        filtered_expenses = expense.find({"user_id": ObjectId(userid), "date": {"$gte": one_week_ago}})
    
    elif filter_value == 'month':
        # Filter by the past month
        one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        filtered_expenses = expense.find({"user_id": ObjectId(userid), "date": {"$gte": one_month_ago}})
    
    else:
        # Route to root
        return redirect(url_for('root'))
    
    ''' Need to implement
    elif filter_value == 'custom':
        three_months_ago = datetime.now(timezone.utc) - timedelta(days=90)
        filtered_expenses = expense.find({"date": {"$gte": three_months_ago}})
    '''

    return render_template('index.html', expense=filtered_expenses)
