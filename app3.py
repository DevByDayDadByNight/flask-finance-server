import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from google_sheets import get_google_sheet
from comparison import compare_and_update_google_sheet

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Configure Google Sheets
SHEET_NAME = 'Finances'  # Google Sheets file name
WORKSHEET_NAME = 'Spend Record'     # Worksheet name (tab name)

def allowed_file(filename):
    """Check if the uploaded file is a valid CSV file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)
