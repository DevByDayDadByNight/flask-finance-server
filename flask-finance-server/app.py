from flask import request, jsonify
from datetime import datetime
from models import Transaction, Category
from db_creator import db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app_creator import app
from flask_migrate import Migrate
from sqlalchemy.dialects.mysql import insert  # Import MySQL-specific insert
from blueprints.category_routes import category_bp
from blueprints.budget_routes import budget_bp
from blueprints.line_item_routes import line_item_bp
from blueprints.transaction_routes import transactions_bp
from blueprints.upload_routes import uploads_bp


# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)





with app.app_context():
    db.create_all()
    Migrate(app, db)
    app.register_blueprint(category_bp, url_prefix="/api")
    app.register_blueprint(budget_bp, url_prefix="/api")
    app.register_blueprint(line_item_bp, url_prefix="/api")
    app.register_blueprint(transactions_bp, url_prefix="/api")
    app.register_blueprint(uploads_bp, url_prefix="/api")


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Replace this with your user verification logic
    if username == "admin" and password == "password":
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)  # Ensure only refresh tokens are allowed here
def refresh():
    current_user = get_jwt_identity()  # Get the identity from the refresh token
    new_access_token = create_access_token(identity=current_user)  # Create a new access token
    refresh_token = create_refresh_token(identity=current_user)
    return jsonify(access_token=new_access_token, refresh_token=refresh_token)