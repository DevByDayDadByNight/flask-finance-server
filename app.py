from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from google_sheets import get_google_sheet
from comparison import compare_and_update_google_sheet
from datetime import datetime
from models import db, Transaction
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import pandas as pd
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "23kl4j2l3k4j234242/4234kl3jlqkjffd&adfkjaljkdflkdjfaljdfalfdadfadfafgafda23kl4j23lk4j2l34jl23kjlksljafoa09801280178r82349678"

jwt = JWTManager(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'  # SQLite for local dev
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Replace this with your user verification logic
    if username == "admin" and password == "password":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401


def fetch_transactions(start_date=None, end_date=None):
    """Fetch transactions optionally filtered by date range."""
    query = Transaction.query

    # Apply date range filters
    if start_date:
        query = query.filter(Transaction.post_date >= datetime.strptime(start_date, "%Y-%m-%d"))
    if end_date:
        query = query.filter(Transaction.post_date <= datetime.strptime(end_date, "%Y-%m-%d"))

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
            "rowNumber": txn.row_number
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

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"msg": "You are not authorized to access this resource"}), 403

    # Check if the file is present
    if 'file' not in request.files:
        return jsonify({"msg": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"msg": "Invalid file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Parse the CSV file
        try:
            df = pd.read_csv(file_path)

            # Ensure required columns exist
            required_columns = ['Transaction Date', 'Post Date', 'Description', 'Amount']
            for col in required_columns:
                if col not in df.columns:
                    return jsonify({"msg": f"Missing column: {col}"}), 400

            # Add transactions, skipping duplicates
            new_transactions = []
            for _, row in df.iterrows():
                # Check for duplicates in the database
                duplicate = Transaction.query.filter_by(
                    post_date=row['Post Date'],
                    description=row['Description'],
                    amount=row['Amount']
                ).first()

                if duplicate:
                    # Skip duplicate transactions
                    continue

                # Add non-duplicate transactions
                transaction = Transaction(
                    transaction_date=row['Transaction Date'],
                    post_date=row['Post Date'],
                    description=row['Description'],
                    amount=row['Amount'],
                    category=row.get('Category')  # Optional column
                )
                new_transactions.append(transaction)

            # Commit new transactions to the database
            db.session.bulk_save_objects(new_transactions)
            db.session.commit()

            return render_template('result.html', new_rows_added=len(new_transactions))

        except Exception as e:
            return jsonify({"msg": f"Error processing file: {str(e)}"}), 500

    return jsonify({"msg": "File upload failed"}), 400

@app.route("/transactions", methods=["POST"])
@jwt_required()
def upload_csv():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"msg": "You are not authorized to access this resource"}), 403

    # Check if file is uploaded
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file provided"}), 400

    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join("uploads", filename)
    os.makedirs("uploads", exist_ok=True)  # Ensure the upload folder exists
    file.save(file_path)

    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Ensure required columns exist
        required_columns = ["Transaction Date", "Post Date", "Description", "Amount"]
        for col in required_columns:
            if col not in df.columns:
                return jsonify({"error": f"Missing required column: {col}"}), 400

        # Process and add transactions to the database
        new_transactions = []
        for _, row in df.iterrows():
            # Check for duplicates in the database
            duplicate = Transaction.query.filter_by(
                post_date=row["Post Date"],
                description=row["Description"],
                amount=row["Amount"]
            ).first()

            if duplicate:
                continue  # Skip duplicates

            # Create a new transaction
            transaction = Transaction(
                transaction_date=row["Transaction Date"],
                post_date=row["Post Date"],
                description=row["Description"],
                amount=row["Amount"],
                category=row.get("Category")  # Optional column
            )
            new_transactions.append(transaction)

        # Bulk insert new transactions
        db.session.bulk_save_objects(new_transactions)
        db.session.commit()

        # Return the count of added transactions
        return jsonify({"message": f"{len(new_transactions)} transactions added successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process the CSV file: {str(e)}"}), 500

def allowed_file(filename):
    """Check if the uploaded file is a valid CSV file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
