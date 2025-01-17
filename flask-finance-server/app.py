from flask import Flask, render_template, request, redirect, url_for, jsonify
from comparison import compare_and_update_google_sheet
from datetime import datetime
from models import Transaction
from db_creator import db
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import os
from app_creator import app
import pandas as pd
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from mysql.connector.errors import IntegrityError as MySQLIntegrityError
from sqlalchemy.dialects.mysql import insert  # Import MySQL-specific insert


import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)





with app.app_context():
    db.create_all()
    Migrate(app, db)

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


def fetch_transactions(start_date=None, end_date=None):
    """Fetch transactions optionally filtered by date range."""
    query = Transaction.query

    # Apply date range filters
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        print("Start Date:", start_date)  # Debug
        query = query.filter(Transaction.post_date >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        print("End Date:", end_date)  # Debug
        query = query.filter(Transaction.post_date <= end_date)

    print(query)
    # Fetch results and convert to a list of dictionaries
    transactions = query.all()
    return [
        {
            "id": txn.id,
            "transactionDate": txn.transaction_date.strftime("%Y-%m-%d") if txn.transaction_date else None,
            "postDate": txn.post_date.strftime("%Y-%m-%d") if txn.post_date else None,
            "description": txn.description,
            "amount": txn.amount,
            "category": txn.category,
            "account": txn.account
        }
        for txn in transactions
    ]

@app.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    transactions = fetch_transactions(start_date=start_date, end_date=end_date)
    return jsonify(transactions)

@app.route('/update_transaction/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    """Update a transaction by ID."""
    try:
        # Retrieve the transaction to update
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Get JSON data from the request
        data = request.json

        # Update fields if they exist in the request
        if "transactionDate" in data:
            transaction.transaction_date = datetime.strptime(data["transactionDate"], "%Y-%m-%d")
        if "postDate" in data:
            transaction.post_date = datetime.strptime(data["postDate"], "%Y-%m-%d")
        if "description" in data:
            transaction.description = data["description"]
        if "amount" in data:
            transaction.amount = float(data["amount"])
        if "category" in data:
            transaction.category = data["category"]
        if "account" in data:
            transaction.account = data["account"]

        # Commit changes to the database
        db.session.commit()

        return jsonify({"message": "Transaction updated successfully"}), 200

    except Exception as e:
        app.logger.error(f"Error updating transaction: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def index():
    """Render the upload form."""
    return render_template('index.html')


import pandas as pd

def deduplicate_csv(df):
    """
    Deduplicate transactions in a CSV file by appending _duplicateX to the Description field.

    Returns:
        pd.DataFrame: A deduplicated DataFrame with updated descriptions for duplicates.
    """
    # Check required columns
    required_columns = ['Transaction Date', 'Post Date', 'Amount', 'Description']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Create a groupby object based on the columns that define uniqueness
    grouped = df.groupby(['Transaction Date', 'Post Date', 'Amount', 'Description'])
    
    # Iterate over each group and handle duplicates
    for _, group in grouped:
        if len(group) > 1:  # Only process duplicates
            for idx, row_index in enumerate(group.index):
                original_description = df.loc[row_index, 'Description']
                df.loc[row_index, 'Description'] = f"{original_description}_duplicate{idx}"
    
    return df

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    # Validate the user's identity (example: only allow 'admin' users to upload CSVs)
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"error": "Unauthorized access"}), 403

    print("oh crap")
    # Validate file existence
    if 'file' not in request.files:
        print("all crap")
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    print("oh ss ", file.filename)
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only .csv files are allowed."}), 400
    print("oh snap")
    # Save the uploaded file
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # Parse the CSV file
        df = pd.read_csv(file_path)
        df = deduplicate_csv(df)
        # Ensure required columns exist
        required_columns = ["Transaction Date", "Post Date", "Description", "Amount"]
        for col in required_columns:
            if col not in df.columns:
                return jsonify({"error": f"Missing column: {col}"}), 400

        # Insert transactions into the database, skipping duplicates
        new_transactions = []
        if 'Account' in df.columns:
            df["Account"] = df["Account"].fillna("")
        
        for _, row in df.iterrows():
             # Convert date strings to Python date objects
            transaction_date = datetime.strptime(row["Transaction Date"], "%m/%d/%Y").date()
            post_date = datetime.strptime(row["Post Date"], "%m/%d/%Y").date()
            account = row.get("Account", "")
            transaction = Transaction(
                transaction_date=transaction_date,
                post_date=post_date,
                description=row["Description"],
                amount=row["Amount"],
                category="",
                account=account
            )
            new_transactions.append(transaction)

        upsert_transactions(new_transactions)

        # Return the count of new transactions added
        return jsonify({
            "message": "CSV uploaded successfully",
            "new_transactions_added": len(new_transactions)
        }), 200
    except (SQLAlchemyIntegrityError, MySQLIntegrityError) as e:
        # Handle the specific IntegrityError

        return jsonify({
            'error': 'IntegrityError',
            'message': str(e),
            'code': 1001  # Your unique error code
        }), 400
    except Exception as e:
        print(f"Error: {e}")
        # Handle any errors during CSV processing
        return jsonify({"error": f"Failed to process the CSV file: {str(e)}"}), 500


def upsert_transactions(transactions):
    """
    Perform a bulk upsert on the Transaction table for MySQL.
    
    Args:
        transactions (list[dict]): List of transactions to insert or update.
    """
    transaction_dicts = [
        {
            "transaction_date": txn.transaction_date,
            "post_date": txn.post_date,
            "description": txn.description,
            "amount": txn.amount,
            "category": txn.category,
            "account": txn.account,
        }
        for txn in transactions
    ]

    # Use INSERT IGNORE for bulk insertion
    stmt = insert(Transaction).values(transaction_dicts).prefix_with("IGNORE")

    # Execute the statement in a transaction
    with db.session.begin():
        db.session.execute(stmt)


def allowed_file(filename):
    """Check if the uploaded file is a valid CSV file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
