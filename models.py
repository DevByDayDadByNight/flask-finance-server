from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_date = db.Column(db.Date, nullable=False)
    post_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)