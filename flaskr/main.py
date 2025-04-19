from flask import Flask

app = Flask(__name__)

@app.route('/')
def root():
    return "Finance Tracker v0.1"