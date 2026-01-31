import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import yaml

def list_sheets():
    config_path = "config/config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    gs_config = config['google_sheet']
    key_path = gs_config['json_key_path']
    sheet_id = gs_config['spreadsheet_id']

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
    client = gspread.authorize(creds)

    sh = client.open_by_key(sheet_id)
    print(f"Spreadsheet Title: {sh.title}")
    print("Available Worksheets:")
    for ws in sh.worksheets():
        print(f" - '{ws.title}'")

if __name__ == "__main__":
    list_sheets()
