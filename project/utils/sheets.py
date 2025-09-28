from typing import List, Dict
from pathlib import Path
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from google.oauth2.service_account import Credentials


class GoogleSheetsClient:
    def __init__(self, creds_path: str,sheet_id:str):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id)

    def get_df(self, worksheet_name: str) -> pd.DataFrame:
        ws = self.sheet.worksheet(worksheet_name)
        return get_as_dataframe(ws)
    
    def update_values(self, worksheet_name: str, range_str: str, values: list[list]):
        """
        Update a range of cells in the specified worksheet.

        :param worksheet_name: Name of the worksheet/tab
        :param range_str: Range string in A1 notation (e.g., "E3:F5")
        :param values: 2D list of values to update
        """
        ws = self.sheet.worksheet(worksheet_name)
        ws.update(range_str, values)
        
    def append_data(self, worksheet_name: str, data: List[Dict]):
        """
        Append rows from list of dicts by just using dict.values() as-is (simple & fast).

        :param worksheet_name: Name of the worksheet/tab
        :param data: List of dictionaries to append
        """
        if not data:
            return

        ws = self.sheet.worksheet(worksheet_name)

        # Convert each dict to list of values in insertion order
        rows = [list(d.values()) for d in data]

        # Append rows in bulk
        ws.append_rows(rows, value_input_option='USER_ENTERED')


if __name__ == '__main__':
    from utils.helers import get_input_values
    BASE_DIR = Path(__file__).parent.parent.parent
    CREDS_PATH = BASE_DIR / 'singular-citron-435211-p7-03fab432846a.json'
    print(CREDS_PATH)

    sheet_id = '1Mf4BbcX2v13x-cY4rEvj-Ez2oel30OKPeU9qnEk_jQA'       # ✅ Sheet ID
    worksheet_name = 'input_sheet'                                       # ✅ Actual tab name

    sheet_client = GoogleSheetsClient(creds_path=CREDS_PATH,sheet_id=sheet_id)
    input_sheet:pd.DataFrame = sheet_client.get_df(worksheet_name)
    
    input_values = get_input_values(input_df=input_sheet)
    print(input_values)
