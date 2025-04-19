from flask import Flask, render_template, request, url_for, redirect, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["tracker"]
collection = db["expense"]

# Base page
@app.route('/', methods=('GET', 'POST'))
def root():
    if request.method=='POST':
        content = request.form['groceries']
        price = int(content)
        collection.insert_one({'groceries': price})
        return redirect(url_for('root'))
    
    return render_template('index.html')

# Read
@app.route('/read', methods=['GET'])
def read():
    data = list(collection.find())
    for d in data:
        d['_id'] = str(d['_id'])
    return jsonify(data)

# Update
@app.route('/users/<id>', methods=['GET','PUT'])
def update_user(id):
    data = request.get_json()
    result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count:
        return jsonify({"msg": "Updated successfully"})
    return jsonify({"error": "User not found"}), 404

# Delete
@app.route('/del/<id>', methods=['GET','DELETE'])
def delete(id):
    result = collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"msg": "Deleted successfully"})
    return jsonify({"error": "User not found"}), 404
