from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
datastore = client.list_database_names()
db = client.tracker
collections = db.list_collection_names()
print(collections)

def show_docs():
    collection = db.expenses
    for doc in collection.find():
        print(doc)

show_docs()