from flask import Flask, render_template, request, redirect, url_for, jsonify
from google_sheets import get_google_sheet
from comparison import compare_and_update_google_sheet
import pandas as pd
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity






app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "23kl4j2l3k4j234242/4234kl3jlqkjffd&adfkjaljkdflkdjfaljdfalfdadfadfafgafda23kl4j23lk4j2l34jl23kjlksljafoa09801280178r82349678"

jwt = JWTManager(app)


# Configure Google Sheets
SHEET_NAME = 'Finances'  # Google Sheets file name
WORKSHEET_NAME = 'Spend Record'     # Worksheet name (tab name)

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


def fetch_transactions(sheet, start_date=None, end_date=None):
    """Fetch transactions optionally filtered by date range, including rowNumber."""
    sheet_data = sheet.get_all_records()
    df = pd.DataFrame(sheet_data)

    # Ensure row numbers are preserved as "rowNumber"
    df.reset_index(inplace=True)  # Reset index to get a numerical row index
    df["rowNumber"] = df.index + 2  # Adjust for 1-based Google Sheets indexing (including header row)

    post_date_column = "Post Date"
    category_column = "Category"

    # Ensure date columns are datetime objects
    if post_date_column in df.columns:
        df[post_date_column] = pd.to_datetime(df[post_date_column], errors="coerce")

    # Preserve null or missing values for the "Category" column
    if category_column in df.columns:
        df[category_column] = df[category_column].fillna("")  # Ensure missing values are explicitly None
    else:
        df[category_column] = ""  # Add "Category" column if it doesn't exist, with all values set to None

    # Filter by date range
    if start_date:
        df = df[df[post_date_column] >= start_date]
    if end_date:
        df = df[df[post_date_column] <= end_date]

    return df.to_dict(orient="records")

@app.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"msg": "You are not authorized to access this resource"}), 403
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
@jwt_required()
def update_transaction(row_number):
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"msg": "You are not authorized to access this resource"}), 403
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
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"msg": "You are not authorized to access this resource"}), 403
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
@jwt_required()
def upload_csv():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"msg": "You are not authorized to access this resource"}), 403
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
