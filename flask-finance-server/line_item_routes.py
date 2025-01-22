from flask import Blueprint, request, jsonify
from db_creator import db
from models import Budget, LineItem

line_item_bp = Blueprint('line_item', __name__)

@line_item_bp.route('/line_items', methods=['GET'])
def get_line_items():
    line_items = LineItem.query.all()
    return jsonify([{
        'id': item.id,
        'budget_id': item.budget_id,
        'amount': item.amount,
        'name': item.name,
        'type': item.type,
        'related_categories': item.related_categories
    } for item in line_items])

@line_item_bp.route('/line_items', methods=['POST'])
def create_line_item():
    data = request.json
    budget = Budget.query.get_or_404(data['budget_id'])
    line_item = LineItem(
        budget_id=budget.id,
        amount=data['amount'],
        name=data['name'],
        type=data['type'],
        related_categories=data.get('related_categories', [])
    )
    db.session.add(line_item)
    db.session.commit()
    return jsonify({'message': 'Line item created', 'id': line_item.id}), 201

@line_item_bp.route('/line_items/<int:id>', methods=['PUT'])
def update_line_item(id):
    data = request.json
    line_item = LineItem.query.get_or_404(id)
    line_item.amount = data['amount']
    line_item.name = data['name']
    line_item.type = data['type']
    line_item.related_categories = data.get('related_categories', [])
    db.session.commit()
    return jsonify({'message': 'Line item updated'})

@line_item_bp.route('/line_items/<int:id>', methods=['DELETE'])
def delete_line_item(id):
    line_item = LineItem.query.get_or_404(id)
    db.session.delete(line_item)
    db.session.commit()
    return jsonify({'message': 'Line item deleted'})
