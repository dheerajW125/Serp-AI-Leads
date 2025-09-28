# Importing required library 
import pygsheets
import pandas as pd
import datetime

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


SERVICE_ACCOUNT_PATH = BASE_DIR / 'singular-citron-435211-p7-03fab432846a.json'

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1Mf4BbcX2v13x-cY4rEvj-Ez2oel30OKPeU9qnEk_jQA/edit?gid=940853107#gid=940853107'


def authorize_and_get_spreadsheet():
    client = pygsheets.authorize(service_account_file=SERVICE_ACCOUNT_PATH) 
    # print(client.spreadsheet_titles()) 
    # spreadsheet = client.open(client.spreadsheet_titles()[0])
    spreadsheet = client.open_by_url(SHEET_URL)
    return spreadsheet

# def create_input_googlesheet(spreadsheet, keyword, pages, prompt):
def create_input_googlesheet(spreadsheet):

    try:
        spreadsheet.add_worksheet(title="input_sheet", rows=200, cols=26, src_tuple=None, src_worksheet=None, index=None)
        ws = spreadsheet.worksheet("title", "input_sheet")
        # date = datetime.datetime.today().strftime("%Y-%m-%d")
        ws.cell("A1").set_text_format("bold", True).value = "Date"
        ws.cell("B1").set_text_format("bold", True).value = "Keyword"
        ws.cell("C1").set_text_format("bold", True).value = "Sector"
        ws.cell("D1").set_text_format("bold", True).value = "Number of google search result pages"
        ws.cell("E1").set_text_format("bold", True).value = "Run"
        ws.cell("F1").set_text_format("bold", True).value = "Stats"
        ws.cell("G1").set_text_format("bold", True).value = "Test prompt"
        ws.adjust_column_width(start=1, end=1, pixel_size=None)
        ws.adjust_column_width(start=2, end=2, pixel_size=None)
        ws.adjust_column_width(start=3, end=3, pixel_size=None)
        ws.adjust_column_width(start=4, end=4, pixel_size=None)
        ws.adjust_column_width(start=5, end=5, pixel_size=None)
        # print(ws.cols)
    except:
        ws = spreadsheet.worksheet("title", "input_sheet")

    # cells = ws.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    # end_row = len(cells)
    # print(end_row)

    # ws.update_values(f"A{end_row+1}", [[keyword]])
    # ws.update_values(f"B{end_row+1}", [[pages]])
    # ws.update_values(f"C{end_row+1}", [[prompt]])
    return ws

def create_output_gsheets(spreadsheet, output):
    df = pd.DataFrame(output)
    # print(df)
    try:
        spreadsheet.add_worksheet(title="output_sheet1", rows=200, cols=26, src_tuple=None, src_worksheet=None, index=None)
        ws = spreadsheet.worksheet("title", "output_sheet1")
        print(ws.cols)
        print(ws.index)
        for col in range(1, ws.cols+1):
            pair = (1,col)
            ws.cell(pair).set_text_format("bold", True)
            ws.adjust_column_width(start=col, end=col, pixel_size=None)
    except:
        ws = spreadsheet.worksheet("title", "output_sheet1")

    cells = ws.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
    end_row = len(cells)
    print(end_row)

    copy_head = False
    if end_row == 1:
        copy_head = True
        start = end_row
    else:
        start = end_row + 1
    ws.set_dataframe(df, start=f'A{start}', copy_index=False, copy_head=copy_head, extend=True, fit=False, escape_formulae=False, nan="")


def update_google_sheet_from_df(sheet, original_df, update_df):
    """
    Updates specific fields in a Google Sheet based on an update DataFrame.

    :param sheet: pygsheets Worksheet object
    :param original_df: DataFrame representing the entire Google Sheet data
    :param update_df: DataFrame containing the updates, with indices matching original_df
    """
    for index, row in update_df.iterrows():
        if index not in original_df.index:
            print(f"Index {index} is not valid in the original DataFrame. Skipping.")
            continue
        
        for field_name, new_value in row.items():
            if field_name not in original_df.columns:
                print(f"Field '{field_name}' does not exist in the original DataFrame. Skipping.")
                continue
            
            # Calculate the cell address in Google Sheets
            col_number = original_df.columns.get_loc(field_name) + 1  # 1-based column indexing
            row_number = index + 2  # Add 2: index starts at 0, and row 1 is the header in Google Sheets
            
            # Update the cell in Google Sheet
            sheet.update_value((row_number, col_number), new_value)
            print(f"Updated cell ({row_number}, {col_number}) to '{new_value}'")

# can give error, so re-enable the api and then retry
# PS C:\Users\mishr\OneDrive\Documents\Swati141024Relu\Serp-AI-Leads\app> py -3.10 gsheets_integrator.py
# ['pygsheet-serpai-swati']

if __name__ == "__main__":

    spreadsheet = authorize_and_get_spreadsheet()

    # create_input_googlesheet(keyword="healthcare staffing companies usa", pages=10, prompt='read the content carefully. check if the content is for a company that provides staffing solutions for the hospitality sector in usa. if yes, then summarize the content as text showing the type of hospitality services they recruit for, otherwise summarize the content text to "not for hospitality sector".')
    # output = [{"link": "content1", "ai_response": "response1"}, {"link": "content2", "ai_response": "response2"}]
    # create_output_gsheets(spreadsheet, output)
    # input_sheet = create_input_googlesheet(spreadsheet)
    # input_df = input_sheet.get_as_df()
    # for index,row in input_df.iterrows():
    #     required_input_df = row.to_dict()
    #     date = required_input_df["Date"]
    #     keyword = required_input_df["Keyword"]
    #     sector = required_input_df["Sector"]
    #     pages = required_input_df["Number of google search result pages"]
    #     prompt = required_input_df["Test prompt"]
    #     print(date, keyword, sector, pages, prompt)

