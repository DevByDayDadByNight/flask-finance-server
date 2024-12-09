import pandas as pd

def compare_and_update_google_sheet(uploaded_csv, google_sheet, comparison_columns):
    """
    Compare the uploaded CSV with the master data in the Google Sheet and append new rows.

    Args:
        uploaded_csv (str): Path to the uploaded CSV file.
        google_sheet (gspread.models.Worksheet): Google Sheets worksheet instance.
        comparison_columns (list): List of columns to use for comparison.

    Returns:
        int: Number of new rows added to the Google Sheet.
    """
    # Load the uploaded CSV into a DataFrame
    uploaded_df = pd.read_csv(uploaded_csv)

    # Get all data from the Google Sheet and load into a DataFrame
    sheet_data = google_sheet.get_all_records()
    sheet_df = pd.DataFrame(sheet_data)

    # Ensure both DataFrames have the required comparison columns
    uploaded_df = uploaded_df[comparison_columns]
    sheet_df = sheet_df[comparison_columns]

   

    # Clean up the data
    # Remove spaces from the 'Description' column
    if 'Description' in comparison_columns:
        uploaded_df['Description'] = uploaded_df['Description'].str.replace(' ', '', regex=False)
        sheet_df['Description'] = sheet_df['Description'].str.replace(' ', '', regex=False)

    # Use absolute values for the 'Amount' column
    if 'Amount' in comparison_columns:
        uploaded_df['Amount'] = uploaded_df['Amount'].abs()
        
        sheet_df['Amount'] = pd.to_numeric(sheet_df['Amount'], errors='coerce').fillna(0)
        print("hit this is amount", sheet_df['Amount'])
        sheet_df['Amount'] = sheet_df['Amount'].abs()

     # Format date columns to MM/DD/YYYY
    date_columns = ['transaction date', 'post date']  # Update with your actual column names
    for col in date_columns:
        if col in uploaded_df.columns:
            uploaded_df[col] = pd.to_datetime(uploaded_df[col], errors='coerce').dt.strftime('%m/%d/%Y')
        if col in sheet_df.columns:
            sheet_df[col] = pd.to_datetime(sheet_df[col], errors='coerce').dt.strftime('%m/%d/%Y')

    # Identify new rows in the uploaded CSV that are not in the Google Sheet
    new_rows = pd.merge(
        uploaded_df, 
        sheet_df, 
        on=comparison_columns, 
        how='left', 
        indicator=True
    )
    new_rows = new_rows[new_rows['_merge'] == 'left_only'].drop(columns=['_merge'])

    # Append new rows to the Google Sheet
    rows_to_append = new_rows.to_dict(orient='records')
    for row in rows_to_append:
        google_sheet.append_row([row[col] for col in comparison_columns])

    # Return the number of rows added
    return len(rows_to_append)

