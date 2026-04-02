
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify([])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return jsonify(data), 201
