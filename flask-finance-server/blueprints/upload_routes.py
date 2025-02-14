from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime
from models import Transaction
from db_creator import db
from sqlalchemy.dialects.mysql import insert

uploads_bp = Blueprint('uploads', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv']

def deduplicate_csv(df):
    required_columns = ['Transaction Date', 'Post Date', 'Amount', 'Description']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    grouped = df.groupby(['Transaction Date', 'Post Date', 'Amount', 'Description'])
    for _, group in grouped:
        if len(group) > 1:
            for idx, row_index in enumerate(group.index):
                original_description = df.loc[row_index, 'Description']
                df.loc[row_index, 'Description'] = f"{original_description}_duplicate{idx}"
    return df

@uploads_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"error": "Unauthorized access"}), 403
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(file_path)
    try:
        df = pd.read_csv(file_path)
        df = deduplicate_csv(df)
        transactions = [
            Transaction(
                transaction_date=datetime.strptime(row["Transaction Date"], "%m/%d/%Y").date(),
                post_date=datetime.strptime(row["Post Date"], "%m/%d/%Y").date(),
                description=row["Description"],
                amount=row["Amount"],
                category=row["Category"],
                account=str(row.get("Account", ""))
            )
            for _, row in df.iterrows()
        ]
        stmt = insert(Transaction).values([{
            "transaction_date": t.transaction_date,
            "post_date": t.post_date,
            "description": t.description,
            "amount": t.amount,
            "category": t.category,
            # insert t.account as string if it exists, else empty string
            "account": "" if t.account == "nan" else t.account
        } for t in transactions]).prefix_with("IGNORE")
        with db.session.begin():
            db.session.execute(stmt)
        return jsonify({"message": "CSV uploaded successfully", "new_transactions_added": len(transactions)}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": f"Failed to process the CSV file: {str(e)}"}), 500
