from db_creator import db
from datetime import date

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