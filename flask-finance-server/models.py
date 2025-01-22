from db_creator import db
from datetime import date
from sqlalchemy.dialects.postgresql import JSON

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, nullable=False)  # Use db.Date for dates
    post_date = db.Column(db.Date, nullable=False)          # Use db.Date for dates
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    account = db.Column(db.String(100), nullable=True)

    # Add a unique constraint
    __table_args__ = (
        db.UniqueConstraint(
            'transaction_date', 'post_date', 'description', 'amount',
            name='uq_transaction'
        ),
    )


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Budget(db.Model):
    __tablename__ = 'budget'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    line_items = db.relationship('LineItem', back_populates='budget', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Budget {self.name}>"

class LineItem(db.Model):
    __tablename__ = 'line_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    related_categories = db.Column(JSON, default=[])

    budget = db.relationship('Budget', back_populates='line_items')

    def __repr__(self):
        return f"<LineItem {self.name}, Amount: {self.amount}>"
