import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up Google Sheets API credentials
GOOGLE_SHEETS_CREDENTIALS_FILE = '/app/service-account-key.json'

def get_google_sheet(sheet_name, worksheet_name):
    """Connect to Google Sheets and fetch a worksheet by name or default to the first one."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS_FILE, scope)
    client = gspread.authorize(credentials)
    
    # Debug: List all spreadsheets
    print("hit about to show shit:", worksheet_name)
    print("Available spreadsheets:", client.openall())
    sheet = client.open(sheet_name)
    
    # Return the specific worksheet by name, or the first one if not specified
    if worksheet_name:
        return sheet.worksheet(worksheet_name)
    else:
        return sheet.sheet1  # Default to the first worksheet
