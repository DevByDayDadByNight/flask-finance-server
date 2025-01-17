from flask_cors import CORS
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import timedelta

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "23kl4j2l3k4j234242/4234kl3jlqkjffd&adfkjaljkdflkdjfaljdfalfdadfadfafgafda23kl4j23lk4j2l34jl23kjlksljafoa09801280178r82349678"

jwt = JWTManager(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'  # SQLite for local dev
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Configure token expiration times
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)  # Access token expires in 15 minutes
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)  # Refresh token expires in 30 days

app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CORS(app)