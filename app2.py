import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Function to check if file is allowed (CSV files only)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to compare two CSV files on concatenated columns
def compare_csvs_on_concatenated_columns(file1, file2, columns_to_compare, output_columns):
    # Load the CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Ensure that the 'Amount' column is treated as an absolute value
    if 'Amount' in columns_to_compare:
        df1['Amount'] = df1['Amount'].abs()
        df2['Amount'] = df2['Amount'].abs()

    # Remove spaces from 'Description' column, if it exists
    if 'Description' in columns_to_compare:
        df1['Description'] = df1['Description'].str.replace(' ', '')
        df2['Description'] = df2['Description'].str.replace(' ', '')

    # Create a new column in both DataFrames by concatenating the specified columns
    df1['concat_column'] = df1[columns_to_compare].astype(str).agg(''.join, axis=1)
    df2['concat_column'] = df2[columns_to_compare].astype(str).agg(''.join, axis=1)

    # Merge the DataFrames on the concatenated column
    merged_df = pd.merge(df1, df2, on='concat_column', how='outer', indicator=True, suffixes=('_x', '_y'))

    # Filter rows that are unique to file2 (right_only)
    unique_to_file2 = merged_df[merged_df['_merge'] == 'right_only']

    # Drop the merge indicator and concatenated column
    unique_to_file2 = unique_to_file2.drop(columns=['_merge', 'concat_column'])

    # Select only the columns from the second file (those suffixed with _y)
    selected_columns = [col for col in unique_to_file2.columns if col.endswith('_y')]

    # Rename the columns by removing the '_y' suffix
    unique_to_file2 = unique_to_file2[selected_columns].rename(columns=lambda col: col.rstrip('_y'))

    # Re-fill NaN values with an empty string (to handle missing values)
    unique_to_file2.fillna('', inplace=True)

    # Reorder columns according to the desired output order
    output_columns = [col for col in output_columns if col in unique_to_file2.columns]
    unique_to_file2 = unique_to_file2[output_columns]

    return unique_to_file2

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        return redirect(request.url)

    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        return redirect(request.url)

    if file1 and allowed_file(file1.filename) and file2 and allowed_file(file2.filename):
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)
        file1_path = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        file2_path = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

        file1.save(file1_path)
        file2.save(file2_path)

        # Define the columns to compare and the output order
        columns_to_compare = ['Transaction Date', 'Post Date', 'Description', 'Amount']
        output_columns = ['Transaction Date', 'Post Date', 'Description', 'Amount', 'Type']

        # Run the comparison
        unique_to_file2 = compare_csvs_on_concatenated_columns(file1_path, file2_path, columns_to_compare, output_columns)

        # Convert result to HTML for rendering in a template
        unique_to_file2_html = unique_to_file2.to_html(classes='table table-striped', index=False)

        return render_template('result.html', table=unique_to_file2_html)

    return redirect(request.url)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)

