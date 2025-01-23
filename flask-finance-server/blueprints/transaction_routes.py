from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import Transaction
from db_creator import db

transactions_bp = Blueprint('transactions', __name__)

def fetch_transactions(start_date=None, end_date=None):
    query = Transaction.query
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(Transaction.post_date >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(Transaction.post_date <= end_date)
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

@transactions_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transactions = fetch_transactions(start_date=start_date, end_date=end_date)
    return jsonify(transactions)

@transactions_bp.route('/update_transaction/<int:transaction_id>', methods=['PUT'])
@jwt_required()
def update_transaction(transaction_id):
    try:
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404
        data = request.json
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
        db.session.commit()
        return jsonify({"message": "Transaction updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    
    
@transactions_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(transaction_id):
    """Delete a transaction by ID."""
    try:
        # Retrieve the transaction to delete
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Delete the transaction from the database
        db.session.delete(transaction)
        db.session.commit()

        return jsonify({"message": "Transaction deleted successfully"}), 200

    except Exception as e:
        # Log and return an error if something goes wrong
        return jsonify({"error": f"Failed to delete transaction: {str(e)}"}), 500