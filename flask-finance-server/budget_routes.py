from flask import Blueprint, request, jsonify
from datetime import datetime
from db_creator import db
from models import Budget

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budgets', methods=['GET'])
def get_budgets():
    budgets = Budget.query.all()
    return jsonify([{
        'id': budget.id,
        'name': budget.name,
        'start_date': budget.start_date.isoformat(),
        'end_date': budget.end_date.isoformat()
    } for budget in budgets])

@budget_bp.route('/budgets', methods=['POST'])
def create_budget():
    data = request.json
    budget = Budget(
        name=data['name'],
        start_date=datetime.fromisoformat(data['start_date']),
        end_date=datetime.fromisoformat(data['end_date'])
    )
    db.session.add(budget)
    db.session.commit()
    return jsonify({'message': 'Budget created', 'id': budget.id}), 201

@budget_bp.route('/budgets/<int:id>', methods=['PUT'])
def update_budget(id):
    data = request.json
    budget = Budget.query.get_or_404(id)
    budget.name = data['name']
    budget.start_date = datetime.fromisoformat(data['start_date'])
    budget.end_date = datetime.fromisoformat(data['end_date'])
    db.session.commit()
    return jsonify({'message': 'Budget updated'})

@budget_bp.route('/budgets/<int:id>', methods=['DELETE'])
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    db.session.delete(budget)
    db.session.commit()
    return jsonify({'message': 'Budget deleted'})
