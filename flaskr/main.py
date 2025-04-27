from flask import Flask, request, session, render_template , url_for, redirect, jsonify, make_response
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime, timezone, timedelta

from functools import wraps
import secrets
import jwt

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(32)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.tracker
expense = db.expenses
user = db.users

# JWT Funcs
def token_gen(userid):
    payload = {
        'user_id': userid,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def token_verify(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        token = request.cookies.get('jwt_token')

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode the token to validate it
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        # Pass the user_id into the route
        return f(current_user_id, *args, **kwargs)

    return decorate

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

        if  user_cred:
            token = token_gen(str(user_cred['_id']))
            session['userid'] = str(user_cred['_id'])
            session['username'] = username

            resp = make_response(redirect(url_for('root')))
            resp.set_cookie('jwt_token', token, httponly=True, secure=False)
            return resp

    return render_template('auth/login.html')

# Make function for logout session
@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('login'))

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
@token_verify
def add_expense(user_id):
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
@token_verify
def delete(user_id):
    expense.delete_one({ '_id' : ObjectId(user_id)})
    return redirect(url_for('root'))

# Update given expense
@app.route('/update/<id>', methods=['POST'])
@token_verify
def update(user_id):
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
    
    elif filter_value == 'custom':
        # Get the start and end dates from the form
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Parse them into datetime objects
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)

            # Query for expenses between the two dates
            filtered_expenses = expense.find({
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            })
        else:
            return "Start and end date required for custom filter", 400

    else:
        # Route to root
        return redirect(url_for('root'))

    return render_template('index.html', expense=filtered_expenses)
