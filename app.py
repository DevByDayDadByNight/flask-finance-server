from flask import Flask, render_template, request, redirect, url_for, jsonify
from google_sheets import get_google_sheet
from comparison import compare_and_update_google_sheet
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Configure Google Sheets
SHEET_NAME = 'Finances'  # Google Sheets file name
WORKSHEET_NAME = 'Spend Record'     # Worksheet name (tab name)

# Utility function to fetch transactions
def fetch_transactions(sheet, start_date=None, end_date=None):
    """Fetch transactions optionally filtered by date range."""
    sheet_data = sheet.get_all_records()
    df = pd.DataFrame(sheet_data)

    # Ensure date columns are datetime objects
    if "Transaction Date" in df.columns:
        df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], errors="coerce")

    # Filter by date range
    if start_date:
        df = df[df["Transaction Date"] >= start_date]
    if end_date:
        df = df[df["Transaction Date"] <= end_date]

    return df.to_dict(orient="records")

@app.route("/transactions", methods=["GET"])
def get_transactions():
    """Fetch transactions within a date range."""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Parse dates
    start_date = pd.to_datetime(start_date, errors="coerce") if start_date else None
    end_date = pd.to_datetime(end_date, errors="coerce") if end_date else None

    # Fetch Google Sheet
    sheet = get_google_sheet(SHEET_NAME, WORKSHEET_NAME)
    transactions = fetch_transactions(sheet, start_date, end_date)

    return jsonify(transactions)

@app.route("/transaction/<int:row_number>", methods=["PUT"])
def update_transaction(row_number):
    """Update a transaction's category."""
    new_category = request.json.get("category")

    if not new_category:
        return jsonify({"error": "Category is required"}), 400

    # Fetch Google Sheet
    sheet = get_google_sheet(SHEET_NAME, WORKSHEET_NAME)
    sheet.update_cell(row_number, 5, new_category)  # Assume "Category" is in column 5

    return jsonify({"message": "Transaction updated successfully"})

@app.route('/')
def index():
    """Render the upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle the CSV upload, compare with Google Sheets, and update the sheet."""
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Connect to Google Sheets and fetch the worksheet
        google_sheet = get_google_sheet(SHEET_NAME, WORKSHEET_NAME)
        
        comparison_columns = ['Transaction Date', 'Post Date', 'Description', 'Amount']
        # Compare and update Google Sheet
        new_rows_added = compare_and_update_google_sheet(file_path, google_sheet, comparison_columns)

        return render_template('result.html', new_rows_added=new_rows_added)

    return redirect(request.url)

@app.route("/transactions", methods=["POST"])
def upload_csv():
    """Upload a CSV file and update Google Sheets."""
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file provided"}), 400

    # Save and process the file
    file_path = f"uploads/{file.filename}"
    file.save(file_path)

    sheet = get_google_sheet(SHEET_NAME, WORKSHEET_NAME)
    comparison_columns = ["Transaction Date", "Post Date", "Description", "Amount"]
    new_rows_added = compare_and_update_google_sheet(file_path, sheet, comparison_columns)

    return jsonify({"message": f"{new_rows_added} transactions added successfully"})

def allowed_file(filename):
    """Check if the uploaded file is a valid CSV file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
