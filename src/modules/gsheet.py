import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config_loader import settings
import os

class GSheetManager:
    def __init__(self):
        self.config = settings.gsheet_config
        self.client = self._connect()
        
        # Open all configured spreadsheets
        self.workbooks = {}
        
        # Load IDs from config
        sheet_ids = self.config.get('ids', {})
        
        for key, sheet_id in sheet_ids.items():
            try:
                self.workbooks[key] = self.client.open_by_key(sheet_id)
                print(f"[Init] Connected to GSheet ({key}): {self.workbooks[key].title}")
            except Exception as e:
                print(f"Error connecting to GSheet ({key}): {e}")
        
        # Column Indices (0-based)
        self.COLUMN_MAP = {
            'testimony': {
                'date': 1,      # B: 방송 일자
                'region': 2,    # C: 국가분류 (Fix: Topic -> Region)
                'country': 3,   # D: 국가
                'city': 4,      # E: 도시
                'age': 5,       # F: 나이
                'gender': 6,    # G: 성별
                'name': 7,      # H: 이름(한글)
                'name_en': 8,   # I: 이름(영문)
                'category': 9,  # J: 구분
                'runtime': 10,  # K: 러닝타임
                'file': 11,     # L: 원본 파일명
                'status': 12,   # M: 처리 상태
                'err_msg': 13,  # N: 에러 메시지
                'final': 14     # O: 최종 파일명
            },
            'mission_news': {
                'date': 1,      # B: 방송일자
                'region': 2,    # C: 국가분류 (New!)
                'country': 3,   # D: 국가
                'name': 4,      # E: 발표자
                'summary': 5,   # F: 요약 (New!)
                'manager': 6,   # G: 담당자
                'status': 7,    # H: 처리 상태
                'file': 8,      # I: 파일명
                'runtime': 9,   # J: 러닝타임
                'err_msg': 10,  # K: 비고
                'final': 8      # I: 최종 파일명
            }
        }

    def _format_date(self, yymmdd):
        """
        Converts '250101' to '2025. 01. 01'
        If invalid, returns original.
        """
        s = str(yymmdd).strip()
        if len(s) == 6 and s.isdigit():
            # Assume 20xx
            return f"20{s[:2]}. {s[2:4]}. {s[4:]}"
        return s

    def _connect(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Check if key file exists
        key_path = self.config['json_key_path']
        if not os.path.exists(key_path):
            print(f"CRITICAL ERROR: Google API Key not found at {key_path}")
            # For development safety, allow continuing but fail on actual calls?
            # Or just crash properly.
            # raise FileNotFoundError(f"Google API Key not found at {key_path}")
            return None # Allow Mock Fallback context to handle this

        creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
        return gspread.authorize(creds)

    def get_pending_rows(self, sheet_type='testimony'):
        """
        Scan the specified sheet (tab) for rows where Status is empty or '대기'.
        sheet_type: 'testimony' or 'mission_news' (mapped in config)
        """
        tab_name = self.config['tabs'].get(sheet_type)
        if not tab_name:
            print(f"Error: Tab name for '{sheet_type}' not found in config.")
            return []

        try:
            workbook = self.workbooks.get(sheet_type)
            if not workbook:
                print(f"Error: Workbook for '{sheet_type}' not initialized.")
                return []
                
            worksheet = workbook.worksheet(tab_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"Error: Worksheet '{tab_name}' not found in '{sheet_type}' sheet.")
            return []

        # [변경] 헤더 중복 문제 해결을 위해 전체 값을 리스트로 가져와서 인덱스로 접근
        all_values = worksheet.get_all_values()
        pending_data = []

        # Get Column Map for this sheet type
        cols = self.COLUMN_MAP.get(sheet_type)
        if not cols:
            print(f"Error: No column mapping for '{sheet_type}'")
            return []

        # Start loop from Row 3 (Index 2) to skip 2 header rows
        for i in range(2, len(all_values)):
            row = all_values[i]
            
            # Safety check: Ensure row is long enough for the max index we need
            max_idx = max(cols.values())
            if len(row) <= max_idx:
                # If row is too short, pad it with empty strings
                row = row + [''] * (max_idx - len(row) + 1)
            
            original_file = row[cols['file']]
            # [기능추가] 파일명에 확장자가 없으면 자동으로 .mp4 붙이기
            if original_file and not original_file.lower().endswith('.mp4'):
                original_file += '.mp4'
            
            status = row[cols['status']]

            if not original_file or original_file.strip() == '':
                continue # Skip rows without file

            if not status or status.strip() == '' or status == '대기' or status == '에러':
                # Extract Metadata
                meta_data = {
                    '방송 일자': row[cols['date']],
                    '국가': row[cols['country']],
                    '지역': row[cols.get('region')], # [New] Fetch Region
                    '이름(한글)': row[cols['name']]
                }

                row_data = {
                    'index': i + 1, # Row number (1-based)
                    'data': meta_data, # Pass metadata dict
                    'file_name': original_file,
                    'tab_name': tab_name,
                    'type': sheet_type
                }
                pending_data.append(row_data)

        return pending_data

    def update_status(self, sheet_type, row_index, status, error_msg=None, new_filename=None, summary_text=None):
        """
        Update a specific row with new status.
        Also handles Summary Logging.
        """
        tab_name = self.config['tabs'].get(sheet_type)
        workbook = self.workbooks.get(sheet_type)
        if not workbook: return
        
        worksheet = workbook.worksheet(tab_name)

        cols = self.COLUMN_MAP.get(sheet_type)
        if not cols: return

        try:
            # Update Status
            worksheet.update_cell(row_index, cols['status'] + 1, status) # +1 for 1-based index
            
            if sheet_type == 'testimony':
                if error_msg:
                     worksheet.update_cell(row_index, cols['err_msg'] + 1, error_msg)
                if new_filename:
                     worksheet.update_cell(row_index, cols['final'] + 1, new_filename)
                
                # [New] Testimony Summary to Separate Tab
                if summary_text and status == "완료":
                    summary_tab_name = self.config['tabs'].get('testimony_summary')
                    if summary_tab_name:
                        try:
                            # Need to fetch Date/Country/Name from the main sheet to copy over?
                            # Or just rely on what we have? 
                            # We don't have the data here conveniently unless we read it or pass it.
                            # Let's read the row to be safe and accurate.
                            row_values = worksheet.row_values(row_index)
                            # Testimony Map: Date=1, Country=3, Name=7 (0-based)
                            # row_values is 0-indexed list of strings
                            
                            # Valid check
                            date_val = row_values[cols['date']] if len(row_values) > cols['date'] else ""
                            country_val = row_values[cols['country']] if len(row_values) > cols['country'] else ""
                            name_val = row_values[cols['name']] if len(row_values) > cols['name'] else ""

                            # Append to Summary Tab
                            sum_sheet = workbook.worksheet(summary_tab_name)
                            # Format: [Date, Country, Name, Summary]
                            sum_sheet.append_row([date_val, country_val, name_val, summary_text])
                            print(f"     ㄴ 요약 탭 기록 완료: {summary_tab_name}")
                        except Exception as ex:
                            print(f"     ⚠️ 요약 탭 기록 실패: {ex}")

            elif sheet_type == 'mission_news':
                # mission_news: Update Status (H)
                # If error, append to Status
                val = status
                if error_msg:
                    val = f"{status}: {error_msg}"
                worksheet.update_cell(row_index, cols['status'] + 1, val)
                
                # Also upate Filename/Runtime if provided (e.g. at completion)
                if new_filename and 'file' in cols:
                     worksheet.update_cell(row_index, cols['file'] + 1, new_filename)
                
                # [New] Update Summary Column (F)
                if summary_text:
                    worksheet.update_cell(row_index, cols['summary'] + 1, summary_text)
                
        except Exception as e:
            print(f"Error updating sheet: {e}")

        print(f"Updated Row {row_index} in {tab_name}: {status}")

    def add_new_row(self, sheet_type, date, country, name, filename, **kwargs):
        """
        Appends a new row with the provided metadata.
        kwargs can handle extra fields like topic, city, age, etc.
        """
        tab_name = self.config['tabs'].get(sheet_type)
        workbook = self.workbooks.get(sheet_type)
        if not workbook: return

        worksheet = workbook.worksheet(tab_name)
        
        cols = self.COLUMN_MAP.get(sheet_type)
        if not cols: return

        # Prepare a row with empty strings up to the max index
        max_idx = max(cols.values())
        new_row = [''] * (max_idx + 1) # 0-based index means size is max_idx + 1
        
        # Fill data
        # Fill data
        
        # [New] Auto Numbering (Column A / Index 0)
        # [New] Auto Numbering (Column A / Index 0)
        if sheet_type == 'mission_news':
            new_row[0] = "=ROW()-1"
        else:
            new_row[0] = "=ROW()-2"

        # Apply Date Formatting for Sheet
        formatted_date = self._format_date(date)

        if sheet_type == 'testimony':
            new_row[cols['date']] = formatted_date
            new_row[cols['region']] = kwargs.get('region', '')
            new_row[cols['country']] = country
            new_row[cols['city']] = kwargs.get('city', '')
            new_row[cols['age']] = kwargs.get('age', '')
            new_row[cols['gender']] = kwargs.get('gender', '')
            new_row[cols['name']] = name
            new_row[cols['name_en']] = kwargs.get('name_en', '')
            new_row[cols['category']] = kwargs.get('category', '')
            new_row[cols['runtime']] = kwargs.get('runtime', '')
            
            new_row[cols['file']] = filename
            new_row[cols['status']] = '대기'
        elif sheet_type == 'mission_news':
            new_row[cols['date']] = formatted_date
            new_row[cols['region']] = kwargs.get('region', '') # C: Region Tag
            new_row[cols['country']] = country
            new_row[cols['name']] = name # Speaker
            new_row[cols['manager']] = kwargs.get('manager', '') # Manager
            new_row[cols['status']] = '대기'
            new_row[cols['file']] = filename
            new_row[cols['runtime']] = kwargs.get('runtime', '')
        
        # Append to sheet (value_input_option='USER_ENTERED' ensures formula parsing)
        worksheet.append_row(new_row, value_input_option='USER_ENTERED')
        print(f"Added New Row to {tab_name}: {filename} (Date: {formatted_date})")

    def get_registered_files(self, sheet_type):
        """
        Returns a list of all filenames currently registered in the sheet.
        """
        tab_name = self.config['tabs'].get(sheet_type)
        workbook = self.workbooks.get(sheet_type)
        if not workbook: return []

        worksheet = workbook.worksheet(tab_name)
        cols = self.COLUMN_MAP.get(sheet_type)
        if not cols: return []

        # Get all values from the file column (adjusted for 1-based index)
        # Note: col_values returns the entire column. 
        # But we used get_all_values() before to handle header duplication issue.
        # Let's stick to get_all_values for safety if header is messy.
        all_values = worksheet.get_all_values()
        filenames = []
        
        file_col_idx = cols['file']
        
        for i in range(2, len(all_values)): # Skip headers
            row = all_values[i]
            if len(row) > file_col_idx:
                fname = row[file_col_idx]
                if fname and fname.strip():
                    filenames.append(fname.strip())
        
        return filenames

class MockGSheetManager:
    """
    Simulates GSheetManager for testing without API keys.
    """
    def __init__(self):
        print("WARNING: Running in MOCK G-SHEET MODE")
        # Fake Database
        self.mock_db = {
            'testimony': [
                {'header': True}, # Row 1
                {'id': 1, 'date': '240101', 'country': 'TestCountry', 'name': 'TestName', '원본 파일명': 'test_video_01.mp4', '처리 상태': '대기'},
                {'id': 2, 'date': '240102', 'country': 'US', 'name': 'John', '원본 파일명': 'missing.mp4', '처리 상태': '대기'},
            ]
        }

    def get_pending_rows(self, sheet_type='testimony'):
        print(f"[Mock] Scanning {sheet_type} for pending rows...")
        rows = self.mock_db.get(sheet_type, [])
        pending = []
        for i, row in enumerate(rows):
            if i == 0: continue # Header
            if row.get('처리 상태') == '대기':
                pending.append({
                    'index': i + 1, # 1-based index
                    'data': row,
                    'file_name': row.get('원본 파일명'),
                    'tab_name': 'MockTab',
                    'type': sheet_type
                })
        return pending

    def update_status(self, sheet_type, row_index, status, error_msg=None, new_filename=None, url=None):
        print(f"[Mock] UPDATE Row {row_index}: Status='{status}' | Error='{error_msg}' | NewFile='{new_filename}'")
        # Update fake db in memory
        rows = self.mock_db.get(sheet_type)
        if rows and row_index - 1 < len(rows):
            rows[row_index - 1]['처리 상태'] = status

