"""
Authentication Service
Provides endpoints for user registration and login using a JSON-based data store.
"""

import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) to allow Vue to communicate with Flask
CORS(app)

# Path to the local JSON data store
DB_FILE = 'users.json'

def read_users() -> list:
    """
    Reads user data from the local JSON file.
    Returns:
        list: A list of user dictionaries.
    """
    if not os.path.exists(DB_FILE):
        return []
    
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return []

def save_user(user_data: dict) -> None:
    """
    Persists a new user record to the JSON file.
    Args:
        user_data (dict): The dictionary containing user details.
    """
    users = read_users()
    users.append(user_data)
    
    with open(DB_FILE, 'w', encoding='utf-8') as file:
        json.dump(users, file, indent=4)

@app.route('/api/register', methods=['POST'])
def register():
    """
    Endpoint to register a new user. 
    Validates if user already exists before saving.
    """
    payload = request.json
    email = payload.get('email')
    
    current_users = read_users()
    
    if any(user.get('email') == email for user in current_users):
        return jsonify({"message": "User already exists"}), 400

    save_user(payload)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    """
    Endpoint to authenticate a user.
    Compares provided credentials against the data store.
    """
    payload = request.json
    email = payload.get('email')
    password = payload.get('password')

    current_users = read_users()

    # Locate user with matching email and password
    user = next(
        (u for u in current_users if u.get('email') == email and u.get('password') == password), 
        None
    )

    if user:
        return jsonify({"message": "Login successful", "user": user}), 200
        
    return jsonify({"message": "Invalid email or password"}), 401

if __name__ == '__main__':
    # Run the Flask application on port 5000
    app.run(debug=True, port=5000)